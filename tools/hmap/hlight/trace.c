// trace.c

#include "light.h"

typedef struct tnode_s
{
	int		type;
	vec3_t	normal;
	vec_t	dist;
	int		children[2];
	int		pad;
} tnode_t;

tnode_t		*tnodes, *tnode_p;

/*
==============
MakeTnode

Converts the disk node structure into the efficient tracing structure
==============
*/
void MakeTnode (int nodenum)
{
	tnode_t			*t;
	dplane_t		*plane;
	int				i;
	dnode_t 		*node;
	
	t = tnode_p++;

	node = dnodes + nodenum;
	plane = dplanes + node->planenum;

	t->type = plane->type;
	VectorCopy (plane->normal, t->normal);
	t->dist = plane->dist;
	
	for (i=0 ; i<2 ; i++)
	{
		if (node->children[i] < 0)
			t->children[i] = dleafs[-node->children[i] - 1].contents;
		else
		{
			t->children[i] = tnode_p - tnodes;
			MakeTnode (node->children[i]);
		}
	}
			
}


/*
=============
MakeTnodes

Loads the node structure out of a .bsp file to be used for light occlusion
=============
*/
void MakeTnodes (dmodel_t *bm)
{
	tnode_p = tnodes = malloc(numnodes * sizeof(tnode_t));

	MakeTnode (0);
}



/*
==============================================================================

LINE TRACING

The major lighting operation is a point to point visibility test, performed
by recursive subdivision of the line by the BSP tree.

==============================================================================
*/

typedef struct
{
	vec3_t	backpt;
	int		side;
	int		node;
} tracestack_t;


/*
==============
TestLine
==============
*/
#if 0
qboolean TestLine (vec3_t start, vec3_t stop)
{
	int				node;
	vec_t			front, back;
	tracestack_t	*tstack_p;
	int				side;
	vec_t 			frontx, fronty, frontz, backx, backy, backz;
	tracestack_t	tracestack[64];
	tnode_t			*tnode;

	frontx = start[0];
	fronty = start[1];
	frontz = start[2];
	backx = stop[0];
	backy = stop[1];
	backz = stop[2];

	tstack_p = tracestack;
	node = 0;

	while (1)
	{
		while (node < 0 && node != CONTENTS_SOLID)
		{
		// pop up the stack for a back side
			tstack_p--;
			if (tstack_p < tracestack)
				return true;
			node = tstack_p->node;

		// set the hit point for this plane

			frontx = backx;
			fronty = backy;
			frontz = backz;

		// go down the back side

			backx = tstack_p->backpt[0];
			backy = tstack_p->backpt[1];
			backz = tstack_p->backpt[2];

			node = tnodes[tstack_p->node].children[!tstack_p->side];
		}

		if (node == CONTENTS_SOLID)
			return false;	// DONE!

		tnode = &tnodes[node];

		switch (tnode->type)
		{
		case PLANE_X:
			front = frontx - tnode->dist;
			back = backx - tnode->dist;
			break;
		case PLANE_Y:
			front = fronty - tnode->dist;
			back = backy - tnode->dist;
			break;
		case PLANE_Z:
			front = frontz - tnode->dist;
			back = backz - tnode->dist;
			break;
		default:
			front = (frontx*tnode->normal[0] + fronty*tnode->normal[1] + frontz*tnode->normal[2]) - tnode->dist;
			back = (backx*tnode->normal[0] + backy*tnode->normal[1] + backz*tnode->normal[2]) - tnode->dist;
			break;
		}

		if (front > -ON_EPSILON && back > -ON_EPSILON)
//		if (front > 0 && back > 0)
		{
			node = tnode->children[0];
			continue;
		}

		if (front < ON_EPSILON && back < ON_EPSILON)
//		if (front <= 0 && back <= 0)
		{
			node = tnode->children[1];
			continue;
		}

		side = front < 0;

		front = front / (front-back);

		tstack_p->node = node;
		tstack_p->side = side;
		tstack_p->backpt[0] = backx;
		tstack_p->backpt[1] = backy;
		tstack_p->backpt[2] = backz;

		tstack_p++;

		backx = frontx + front*(backx-frontx);
		backy = fronty + front*(backy-fronty);
		backz = frontz + front*(backz-frontz);

		node = tnode->children[side];
	}
}
#elif 1

#define TESTLINESTATE_BLOCKED 0
#define TESTLINESTATE_EMPTY 1
#define TESTLINESTATE_SOLID 2

// LordHavoc: TestLine returns true if there is no impact,
// see below for precise definition of impact (important)
vec3_t testlineimpact;
qboolean RecursiveTestLine (int num, vec3_t p1, vec3_t p2)
{
	int			side, ret;
	vec_t		t1, t2, frac;
	vec3_t		mid;
	tnode_t		*tnode;

	// LordHavoc: this function operates by doing depth-first front-to-back
	// recursion through the BSP tree, checking at every split for a empty to solid
	// transition (impact) in the children, and returns false if one is found

	// LordHavoc: note: 'no impact' does not mean it is empty, it occurs when there
	// is no transition from empty to solid; all solid or a transition from solid
	// to empty are not considered impacts. (this does mean that tracing is not
	// symmetrical; point A to point B may have different results than point B to
	// point A, if either start in solid)

	// check for empty
loc0:
	if (num < 0)
	{
		if (num == CONTENTS_SOLID)
			return TESTLINESTATE_SOLID;
		else
			return TESTLINESTATE_EMPTY;
	}

	// find the point distances
	tnode = tnodes + num;

	if (tnode->type < 3)
	{
		t1 = p1[tnode->type] - tnode->dist;
		t2 = p2[tnode->type] - tnode->dist;
	}
	else
	{
		t1 = DotProduct (tnode->normal, p1) - tnode->dist;
		t2 = DotProduct (tnode->normal, p2) - tnode->dist;
	}

	if (t1 >= 0)
	{
		if (t2 >= 0)
		{
			num = tnode->children[0];
			goto loc0;
		}
		side = 0;
	}
	else
	{
		if (t2 < 0)
		{
			num = tnode->children[1];
			goto loc0;
		}
		side = 1;
	}

	frac = t1 / (t1 - t2);
	mid[0] = p1[0] + frac * (p2[0] - p1[0]);
	mid[1] = p1[1] + frac * (p2[1] - p1[1]);
	mid[2] = p1[2] + frac * (p2[2] - p1[2]);

	// front side first
	ret = RecursiveTestLine (tnode->children[side], p1, mid);
	if (ret != TESTLINESTATE_EMPTY)
		return ret; // solid or blocked
	ret = RecursiveTestLine (tnode->children[!side], mid, p2);
	if (ret != TESTLINESTATE_SOLID)
		return ret; // empty or blocked
	VectorCopy(mid, testlineimpact);
	return TESTLINESTATE_BLOCKED;
}

qboolean TestLine (vec3_t start, vec3_t end)
{
	return RecursiveTestLine(0, start, end) != TESTLINESTATE_BLOCKED;
}
#else
typedef struct
{
	vec3_t	p1, p2, mid;
	int		side;
	int		num;
	int		returnpoint;
} newtracestack_t;

// LordHavoc: TestLine returns true if there is no impact,
// see below for precise definition of impact (important)
qboolean TestLine (vec3_t start, vec3_t end)
{
	newtracestack_t tracestack[256], *stack;
	int			ret;
	vec_t		t1, t2, frac;
	tnode_t		*tnode;

	// LordHavoc: this function operates by doing depth-first front-to-back
	// recursion through the BSP tree, checking at every split for a empty to solid
	// transition (impact) in the children, and returns false if one is found

	// LordHavoc: note: 'no impact' does not mean it is empty, it occurs when there
	// is no transition from empty to solid; all solid or a transition from solid
	// to empty are not considered impacts. (this does mean that tracing is not
	// symmetrical; point A to point B may have different results than point B to
	// point A, if either start in solid)

	stack = tracestack;
	VectorCopy(start, stack->p1);
	VectorCopy(end, stack->p2);
	stack->num = 0;
	stack->returnpoint = 0;

loc3:
	// check for empty
	if (stack->num < 0)
	{
		if (stack->num == CONTENTS_SOLID)
			ret = TESTLINESTATE_SOLID;
		else
			ret = TESTLINESTATE_EMPTY;
		stack--;
		if (stack < tracestack)
			return true; // no impact
		if (stack->returnpoint)
			goto loc2;
		else
			goto loc1;
	}

loc0:
	// find the point distances
	tnode = tnodes + stack->num;

	if (tnode->type < 3)
	{
		t1 = stack->p1[tnode->type] - tnode->dist;
		t2 = stack->p2[tnode->type] - tnode->dist;
	}
	else
	{
		t1 = DotProduct (tnode->normal, stack->p1) - tnode->dist;
		t2 = DotProduct (tnode->normal, stack->p2) - tnode->dist;
	}

	if (t1 >= 0)
	{
		if (t2 >= 0)
		{
			stack->num = tnode->children[0];
			goto loc3;
		}
		stack->side = 0;
	}
	else
	{
		if (t2 < 0)
		{
			stack->num = tnode->children[1];
			goto loc3;
		}
		stack->side = 1;
	}

	frac = t1 / (t1 - t2);
	stack->mid[0] = stack->p1[0] + frac * (stack->p2[0] - stack->p1[0]);
	stack->mid[1] = stack->p1[1] + frac * (stack->p2[1] - stack->p1[1]);
	stack->mid[2] = stack->p1[2] + frac * (stack->p2[2] - stack->p1[2]);

	// front side first
//	ret = RecursiveTestLine (tnode->children[side], p1, mid);
//	if (ret != TESTLINESTATE_EMPTY)
//			return ret; // solid or blocked
	if (tnode->children[stack->side] < 0)
	{
		if (tnode->children[stack->side] == CONTENTS_SOLID)
		{
			stack--;
			if (stack < tracestack)
				return true; // no impact
			if (stack->returnpoint)
				goto loc2;
			else
				goto loc1;
		}
	}
	else
	{
		stack->returnpoint = 0;
		VectorCopy(stack->p1, stack[1].p1);
		VectorCopy(stack->mid, stack[1].p2);
		stack[1].num = tnode->children[stack->side];
		stack++;
		goto loc0;
loc1:
		tnode = tnodes + stack->num;
		if (ret != TESTLINESTATE_EMPTY)
		{
			stack--;
			if (stack < tracestack)
				return true; // no impact
			if (stack->returnpoint)
				goto loc2;
			else
				goto loc1;
		}
	}
//	ret = RecursiveTestLine (tnode->children[!side], mid, p2);
//	if (ret != TESTLINESTATE_SOLID)
//		return ret; // empty or blocked
	if (tnode->children[!stack->side] < 0)
	{
		if (tnode->children[!stack->side] != CONTENTS_SOLID)
		{
			stack--;
			if (stack < tracestack)
				return true; // no impact
			if (stack->returnpoint)
				goto loc2;
			else
				goto loc1;
		}
	}
	else
	{
		stack->returnpoint = 1;

		VectorCopy(stack->mid, stack[1].p1);
		VectorCopy(stack->p2, stack[1].p2);
		stack[1].num = tnode->children[!stack->side];
		stack++;
		goto loc0;
loc2:
		tnode = tnodes + stack->num;
		if (ret != TESTLINESTATE_SOLID)
		{
			stack--;
			if (stack < tracestack)
				return true; // no impact
			if (stack->returnpoint)
				goto loc2;
			else
				goto loc1;
		}
	}
	return false;
}
#endif
