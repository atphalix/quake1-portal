// brush.c

#include "bsp5.h"

int			numbrushplanes;
plane_t		planes[MAX_MAP_PLANES];

int			numbrushfaces;
mface_t		faces[MAX_FACES];		// beveled clipping hull can generate many extra

entity_t *CurrentEntity;

/*
=================
CheckFace

Note: this will not catch 0 area polygons
LordHavoc: actually it does, by checking for degenerate edges
=================
*/
void CheckFace (face_t *f)
{
	int		i, j;
	vec_t	*p1, *p2;
	vec_t	d, edgedist;
	vec3_t	dir, edgenormal, facenormal;

	if (f->numpoints < 3)
		Error ("CheckFace: %i points at %f %f %f",f->numpoints, f->pts[0], f->pts[1], f->pts[2]);

	VectorCopy (planes[f->planenum].normal, facenormal);
	if (f->planeside)
	{
		VectorNegate (facenormal, facenormal);
	}

	for (i=0 ; i<f->numpoints ; i++)
	{
		p1 = f->pts[i];

		for (j=0 ; j<3 ; j++)
			if (p1[j] > BOGUS_RANGE || p1[j] < -BOGUS_RANGE)
				Error ("CheckFace: BOGUS_RANGE: %f %f %f", p1[0], p1[1], p1[2]);

		if (DotProduct(planes[f->planenum].normal, planes[f->planenum].normal) < (1.0 - ON_EPSILON))
			Error ("Checkface: invalid normal (%f %f %f)\n", planes[f->planenum].normal);

		j = i+1 == f->numpoints ? 0 : i+1;

		// check the point is on the face plane
		d = DotProduct (p1, planes[f->planenum].normal) - planes[f->planenum].dist;
		if (d < -ON_EPSILON || d > ON_EPSILON)
			printf ("CheckFace: point off plane at %f %f %f, correcting\n", p1[0], p1[1], p1[2]);
		// correct it even if we did not warn
		d = -d;
		VectorMA(p1, d, planes[f->planenum].normal, p1);

		// check the edge isn't degenerate
		p2 = f->pts[j];
		VectorSubtract (p2, p1, dir);

		if (VectorLength (dir) < ON_EPSILON)
			Error ("CheckFace: degenerate edge at %f %f %f", p2[0], p2[1], p2[2]);

		CrossProduct (facenormal, dir, edgenormal);
		VectorNormalize (edgenormal);
		edgedist = DotProduct (p1, edgenormal);
		edgedist += ON_EPSILON;

		// all other points must be on front side
		for (j=0 ; j<f->numpoints ; j++)
		{
			if (j == i)
				continue;
			d = DotProduct (f->pts[j], edgenormal);
			if (d > edgedist)
				Error ("CheckFace: non-convex at %f %f %f", f->pts[j][0], f->pts[j][1], f->pts[j][2]);
		}
	}
}


//===========================================================================

/*
=================
ClearBounds
=================
*/
void ClearBounds (brushset_t *bs)
{
	int		i, j;

	for (j=0 ; j<NUM_HULLS ; j++)
		for (i=0 ; i<3 ; i++)
		{
			bs->mins[i] = BOGUS_RANGE;
			bs->maxs[i] = -BOGUS_RANGE;
		}
}

/*
=================
AddToBounds
=================
*/
void AddToBounds (brushset_t *bs, vec3_t v)
{
	int		i;

	for (i=0 ; i<3 ; i++)
	{
		if (v[i] < bs->mins[i])
			bs->mins[i] = v[i];
		if (v[i] > bs->maxs[i])
			bs->maxs[i] = v[i];
	}
}

//===========================================================================

int	PlaneTypeForNormal (vec3_t normal)
{
	double	ax, ay, az;

	// NOTE: should these have an epsilon around 1.0?
	if (normal[0] == 1.0)
		return PLANE_X;
	if (normal[1] == 1.0)
		return PLANE_Y;
	if (normal[2] == 1.0)
		return PLANE_Z;
	if (normal[0] == -1.0 || normal[1] == -1.0 || normal[2] == -1.0)
		Error ("PlaneTypeForNormal: not a canonical vector (%f %f %f)", normal[0], normal[1], normal[2]);

	ax = fabs(normal[0]);
	ay = fabs(normal[1]);
	az = fabs(normal[2]);

	if (ax >= ay && ax >= az)
		return PLANE_ANYX;
	if (ay >= ax && ay >= az)
		return PLANE_ANYY;
	return PLANE_ANYZ;
}

#define	DISTEPSILON		0.01
#define	ANGLEEPSILON	0.00001

void NormalizePlane (plane_t *dp)
{
	vec_t	ax, ay, az;

	if (dp->normal[0] == -1.0)
	{
		dp->normal[0] = 1.0;
		dp->dist = -dp->dist;
	}
	else if (dp->normal[1] == -1.0)
	{
		dp->normal[1] = 1.0;
		dp->dist = -dp->dist;
	}
	else if (dp->normal[2] == -1.0)
	{
		dp->normal[2] = 1.0;
		dp->dist = -dp->dist;
	}

	if (dp->normal[0] == 1.0)
	{
		dp->type = PLANE_X;
		return;
	}
	if (dp->normal[1] == 1.0)
	{
		dp->type = PLANE_Y;
		return;
	}
	if (dp->normal[2] == 1.0)
	{
		dp->type = PLANE_Z;
		return;
	}

	ax = fabs(dp->normal[0]);
	ay = fabs(dp->normal[1]);
	az = fabs(dp->normal[2]);

	if (ax >= ay && ax >= az)
		dp->type = PLANE_ANYX;
	else if (ay >= ax && ay >= az)
		dp->type = PLANE_ANYY;
	else
		dp->type = PLANE_ANYZ;
	if (dp->normal[dp->type-PLANE_ANYX] < 0)
	{
		VectorNegate (dp->normal, dp->normal);
		dp->dist = -dp->dist;
	}

}

/*
===============
FindPlane

Returns a global plane number and the side that will be the front
===============
*/
int	FindPlane (plane_t *dplane, int *side)
{
	int			i;
	plane_t		*dp, pl;
	vec_t		dot;

	pl = *dplane;
	NormalizePlane (&pl);
	if (DotProduct(pl.normal, dplane->normal) > 0)
		*side = 0;
	else
		*side = 1;

	dp = planes;
	for (i=0 ; i<numbrushplanes;i++, dp++)
		if (DotProduct (dp->normal, pl.normal) > 1.0 - ANGLEEPSILON && fabs(dp->dist - pl.dist) < DISTEPSILON )
			return i; // regular match

	if (numbrushplanes == MAX_MAP_PLANES)
		Error ("FindPlane: numbrushplanes == MAX_MAP_PLANES");

	dot = VectorLength(dplane->normal);
	if (dot < 1.0 - ANGLEEPSILON || dot > 1.0 + ANGLEEPSILON)
		Error ("FindPlane: normalization error (%f %f %f, length %f)", dplane->normal[0], dplane->normal[1], dplane->normal[2], dot);

	planes[numbrushplanes] = pl;
	numbrushplanes++;

	return numbrushplanes-1;
}


/*
=============================================================================

TURN BRUSHES INTO GROUPS OF FACES

=============================================================================
*/

vec3_t		brush_mins, brush_maxs;
face_t		*brush_faces;

entity_t *FindTargetEntity(char *targetname)
{
	int			entnum;

	for (entnum = 0;entnum < num_entities;entnum++)
		if (!strcmp(targetname, ValueForKey(&entities[entnum], "targetname")))
			return &entities[entnum];
	return NULL;
}

/*
=================
CreateBrushFaces
=================
*/
#define	ZERO_EPSILON	0.001
void CreateBrushFaces (void)
{
	int				i,j, k, rotate;
	vec_t			r;
	face_t			*f;
	winding_t		*w;
	plane_t			plane;
	mface_t			*mf;
	vec3_t			offset, point;

	offset[0] = offset[1] = offset[2] = 0;
	brush_mins[0] = brush_mins[1] = brush_mins[2] = BOGUS_RANGE;
	brush_maxs[0] = brush_maxs[1] = brush_maxs[2] = -BOGUS_RANGE;

	brush_faces = NULL;

	rotate = !strncmp(ValueForKey(CurrentEntity, "classname"), "rotate_", 7);
	if (rotate)
	{
		entity_t	*FoundEntity;
		char 		*searchstring;
		char		text[20];

		searchstring = ValueForKey (CurrentEntity, "target");
		FoundEntity = FindTargetEntity(searchstring);
		if (FoundEntity)
			GetVectorForKey(FoundEntity, "origin", offset);

		sprintf(text, "%g %g %g", offset[0], offset[1], offset[2]);
		SetKeyValue(CurrentEntity, "origin", text);
	}

	for (i = 0;i < numbrushfaces;i++)
	{
		mf = &faces[i];

		w = BaseWindingForPlane (&mf->plane);

		for (j = 0;j < numbrushfaces && w;j++)
		{
			if (j == i)
				continue;
			// flip the plane, because we want to keep the back side
			VectorNegate(faces[j].plane.normal, plane.normal);
			plane.dist = -faces[j].plane.dist;

			w = ClipWinding (w, &plane, true);
		}

		if (!w)
			continue;	// overcontrained plane

		// this face is a keeper
		f = AllocFace ();
		f->numpoints = w->numpoints;
		if (f->numpoints > MAXEDGES)
			Error ("CreateBrushFaces: f->numpoints > MAXEDGES");

		for (j = 0;j < w->numpoints;j++)
		{
			for (k = 0;k < 3;k++)
			{
				point[k] = w->points[j][k] - offset[k];
				r = Q_rint (point[k]);
				if ( fabs(point[k] - r) < ZERO_EPSILON)
					f->pts[j][k] = r;
				else
					f->pts[j][k] = point[k];

				if (f->pts[j][k] < brush_mins[k])
					brush_mins[k] = f->pts[j][k];
				if (f->pts[j][k] > brush_maxs[k])
					brush_maxs[k] = f->pts[j][k];
			}

		}
		VectorCopy (mf->plane.normal, plane.normal);
		VectorScale (mf->plane.normal, mf->plane.dist, point);
		VectorSubtract (point, offset, point);
		plane.dist = DotProduct (plane.normal, point);

		FreeWinding (w);
		f->texturenum = mf->texinfo;
		f->planenum = FindPlane (&plane, &f->planeside);
//      f->planenum = FindPlane (&mf->plane, &f->planeside);
		f->next = brush_faces;
		brush_faces = f;
		CheckFace (f);
	}

	// Rotatable objects have to have a bounding box big enough
	// to account for all its rotations.
	if (rotate)
	{
		vec_t delta, min, max;

		min = brush_mins[0];
		if (min > brush_mins[1])
			min = brush_mins[1];
		if (min > brush_mins[2])
			min = brush_mins[2];

		max = brush_maxs[0];
		if (max > brush_maxs[1])
			max = brush_maxs[1];
		if (max > brush_maxs[2])
			max = brush_maxs[2];

		delta = fabs(max);
		if (fabs(min) > delta)
			delta = fabs(min);

		for (k = 0;k < 3;k++)
		{
			brush_mins[k] = -delta;
			brush_maxs[k] = delta;
		}
	}
}



/*
==============================================================================

BEVELED CLIPPING HULL GENERATION

This is done by brute force, and could easily get a lot faster if anyone cares.
==============================================================================
*/

vec3_t	hull_size[3][2] =
{
{{  0,  0,  0}, {  0,  0,  0}},
{{-16,-16,-32}, { 16, 16, 24}},
{{-32,-32,-64}, { 32, 32, 24}}
};

// LordHavoc: these were 32 and 64 respectively
#define	MAX_HULL_POINTS	512
#define	MAX_HULL_EDGES	1024

int		num_hull_points;
vec3_t	hull_points[MAX_HULL_POINTS];
vec3_t	hull_corners[MAX_HULL_POINTS*8];
int		num_hull_edges;
int		hull_edges[MAX_HULL_EDGES][2];

/*
============
AddBrushPlane
=============
*/
void AddBrushPlane (plane_t *plane)
{
	int		i;
	plane_t	*pl;
	double	l;

	if (numbrushfaces == MAX_FACES)
		Error ("AddBrushPlane: numbrushfaces == MAX_FACES");
	l = VectorLength (plane->normal);
	if (l < 0.999 || l > 1.001)
		Error ("AddBrushPlane: bad normal (%f %f %f, length %f)", plane->normal[0], plane->normal[1], plane->normal[2], l);

	for (i=0 ; i<numbrushfaces ; i++)
	{
		pl = &faces[i].plane;
		if (VectorCompare (pl->normal, plane->normal) && fabs(pl->dist - plane->dist) < ON_EPSILON)
			return;
	}
	faces[i].plane = *plane;
	faces[i].texinfo = faces[0].texinfo;
	numbrushfaces++;
}


/*
============
TestAddPlane

Adds the given plane to the brush description if all of the original brush
vertexes can be put on the front side
=============
*/
void TestAddPlane (plane_t *plane)
{
	int		i, c;
	vec_t	d;
	vec_t	*corner;
	plane_t	flip;
	vec3_t	inv;
	int		counts[3];
	plane_t	*pl;

	// see if the plane has allready been added
	for (i=0 ; i<numbrushfaces ; i++)
	{
		pl = &faces[i].plane;
		if (VectorCompare (plane->normal, pl->normal) && fabs(plane->dist - pl->dist) < ON_EPSILON)
			return;
		VectorNegate (plane->normal, inv);
		if (VectorCompare (inv, pl->normal) && fabs(plane->dist + pl->dist) < ON_EPSILON)
			return;
	}

	// check all the corner points
	counts[0] = counts[1] = counts[2] = 0;
	c = num_hull_points * 8;

	corner = hull_corners[0];
	for (i=0 ; i<c ; i++, corner += 3)
	{
		d = DotProduct (corner, plane->normal) - plane->dist;
		if (d < -ON_EPSILON)
		{
			if (counts[0])
				return;
			counts[1]++;
		}
		else if (d > ON_EPSILON)
		{
			if (counts[1])
				return;
			counts[0]++;
		}
		else
			counts[2]++;
	}

	// the plane is a seperator

	if (counts[0])
	{
		VectorNegate (plane->normal, flip.normal);
		flip.dist = -plane->dist;
		plane = &flip;
	}

	AddBrushPlane (plane);
}

/*
============
AddHullPoint

Doesn't add if duplicated
=============
*/
int AddHullPoint (vec3_t p, int hullnum)
{
	int		i;
	vec_t	*c;
	int		x,y,z;

	for (i=0 ; i<num_hull_points ; i++)
		if (VectorCompare (p, hull_points[i]))
			return i;

	VectorCopy (p, hull_points[num_hull_points]);

	c = hull_corners[i*8];

	for (x=0 ; x<2 ; x++)
		for (y=0 ; y<2 ; y++)
			for (z=0; z<2 ; z++)
			{
				c[0] = p[0] + hull_size[hullnum][x][0];
				c[1] = p[1] + hull_size[hullnum][y][1];
				c[2] = p[2] + hull_size[hullnum][z][2];
				c += 3;
			}

	if (num_hull_points == MAX_HULL_POINTS)
		Error ("AddHullPoint: MAX_HULL_POINTS");

	num_hull_points++;

	return i;
}


/*
============
AddHullEdge

Creates all of the hull planes around the given edge, if not done allready
=============
*/
void AddHullEdge (vec3_t p1, vec3_t p2, int hullnum)
{
	int		pt1, pt2;
	int		i;
	int		a, b, c, d, e;
	vec3_t	edgevec, planeorg, planevec;
	plane_t	plane;
	vec_t	l;

	pt1 = AddHullPoint (p1, hullnum);
	pt2 = AddHullPoint (p2, hullnum);

	for (i=0 ; i<num_hull_edges ; i++)
		if ((hull_edges[i][0] == pt1 && hull_edges[i][1] == pt2) || (hull_edges[i][0] == pt2 && hull_edges[i][1] == pt1))
			return;	// already added

	if (num_hull_edges == MAX_HULL_EDGES)
		Error ("AddHullEdge: MAX_HULL_EDGES");

	hull_edges[i][0] = pt1;
	hull_edges[i][1] = pt2;
	num_hull_edges++;

	VectorSubtract (p1, p2, edgevec);
	VectorNormalize (edgevec);

	for (a=0 ; a<3 ; a++)
	{
		b = (a+1)%3;
		c = (a+2)%3;
		for (d=0 ; d<=1 ; d++)
			for (e=0 ; e<=1 ; e++)
			{
				VectorCopy (p1, planeorg);
				planeorg[b] += hull_size[hullnum][d][b];
				planeorg[c] += hull_size[hullnum][e][c];

				VectorClear (planevec);
				planevec[a] = 1;

				CrossProduct (planevec, edgevec, plane.normal);
				l = VectorLength (plane.normal);
				if (l < 1-ANGLEEPSILON || l > 1+ANGLEEPSILON)
					continue;
				plane.dist = DotProduct (planeorg, plane.normal);
				TestAddPlane (&plane);
			}
	}
}

/*
============
ExpandBrush
=============
*/
void ExpandBrush (int hullnum)
{
	int		i, x, s;
	vec3_t	corner;
	face_t	*f;
	plane_t	plane, *p;

	num_hull_points = 0;
	num_hull_edges = 0;

	// create all the hull points
	for (f=brush_faces ; f ; f=f->next)
		for (i=0 ; i<f->numpoints ; i++)
			AddHullPoint (f->pts[i], hullnum);

	// expand all of the planes
	for (i=0 ; i<numbrushfaces ; i++)
	{
		p = &faces[i].plane;
		VectorClear (corner);
		for (x=0 ; x<3 ; x++)
		{
			if (p->normal[x] > 0)
				corner[x] = hull_size[hullnum][1][x];
			else if (p->normal[x] < 0)
				corner[x] = hull_size[hullnum][0][x];
		}
		p->dist += DotProduct (corner, p->normal);
	}

	// add any axis planes not contained in the brush to bevel off corners
	for (x=0 ; x<3 ; x++)
		for (s=-1 ; s<=1 ; s+=2)
		{
			// add the plane
			VectorClear (plane.normal);
			plane.normal[x] = s;
			if (s == -1)
				plane.dist = -brush_mins[x] + -hull_size[hullnum][0][x];
			else
				plane.dist = brush_maxs[x] + hull_size[hullnum][1][x];
			AddBrushPlane (&plane);
		}

	// add all of the edge bevels
	for (f=brush_faces ; f ; f=f->next)
		for (i=0 ; i<f->numpoints ; i++)
			AddHullEdge (f->pts[i], f->pts[(i+1)%f->numpoints], hullnum);
}

//============================================================================


/*
===============
LoadBrush

Converts a mapbrush to a bsp brush
===============
*/
brush_t *LoadBrush (mbrush_t *mb, int hullnum)
{
	brush_t		*b;
	int			contents;
	char		*name;
	mface_t		*f;

	//
	// check texture name for attributes
	//
	name = miptex[texinfo[mb->faces->texinfo].miptex];

	if (!Q_strcasecmp(name, "clip") && hullnum == 0)
		return NULL;		// "clip" brushes don't show up in the draw hull

	if (name[0] == '*' && worldmodel)		// entities never use water merging
	{
		if (!Q_strncasecmp(name+1,"lava",4))
			contents = CONTENTS_LAVA;
		else if (!Q_strncasecmp(name+1,"slime",5))
			contents = CONTENTS_SLIME;
		else
			contents = CONTENTS_WATER;
	}
	else if (!Q_strncasecmp (name, "sky",3) && worldmodel && hullnum == 0)
		contents = CONTENTS_SKY;
	else
		contents = CONTENTS_SOLID;

	if (hullnum && contents != CONTENTS_SOLID && contents != CONTENTS_SKY)
		return NULL;		// water brushes don't show up in clipping hulls

	// no seperate textures on clip hull

	//
	// create the faces
	//
	brush_faces = NULL;

	numbrushfaces = 0;
	for (f=mb->faces ; f ; f=f->next)
	{
		faces[numbrushfaces] = *f;
		if (hullnum)
			faces[numbrushfaces].texinfo = 0;
		numbrushfaces++;
	}

	CreateBrushFaces ();

	if (!brush_faces)
	{
		printf ("WARNING: couldn't create brush faces\n");
		return NULL;
	}

	if (hullnum)
	{
		ExpandBrush (hullnum);
		CreateBrushFaces ();
	}

	//
	// create the brush
	//
	b = AllocBrush ();

	b->contents = contents;
	b->faces = brush_faces;
	VectorCopy (brush_mins, b->mins);
	VectorCopy (brush_maxs, b->maxs);

	return b;
}

//=============================================================================


/*
============
Brush_DrawAll

============
*/
void Brush_DrawAll (brushset_t *bs)
{
	brush_t	*b;
	face_t	*f;

	for (b=bs->brushes ; b ; b=b->next)
		for (f=b->faces ; f ; f=f->next)
			Draw_DrawFace (f);
}


/*
============
Brush_LoadEntity
============
*/
brushset_t *Brush_LoadEntity (entity_t *ent, int hullnum)
{
	brush_t		*b, *next, *water, *other;
	mbrush_t	*mbr;
	int			numbrushes;
	brushset_t	*bset;

	bset = malloc (sizeof(brushset_t));
	memset (bset, 0, sizeof(brushset_t));
	ClearBounds (bset);

	numbrushes = 0;
	other = water = NULL;

	qprintf ("--- Brush_LoadEntity ---\n");

	CurrentEntity = ent;

	for (mbr = ent->brushes ; mbr ; mbr=mbr->next)
	{
		b = LoadBrush (mbr, hullnum);
		if (!b)
			continue;

		numbrushes++;

		if (b->contents != CONTENTS_SOLID)
		{
			b->next = water;
			water = b;
		}
		else
		{
			b->next = other;
			other = b;
		}

		AddToBounds (bset, b->mins);
		AddToBounds (bset, b->maxs);
	}

	// add all of the water textures at the start
	for (b=water ; b ; b=next)
	{
		next = b->next;
		b->next = other;
		other = b;
	}

	bset->brushes = other;

	brushset = bset;
	Brush_DrawAll (bset);

	qprintf ("%i brushes read\n",numbrushes);

	return bset;
}


