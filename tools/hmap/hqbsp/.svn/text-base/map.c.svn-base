// map.c

#include "bsp5.h"

// just for statistics
int			nummapbrushfaces = 0;

int			nummapbrushes = 0;
mbrush_t	mapbrushes[MAX_MAP_BRUSHES];

int			num_entities = 0;
entity_t	entities[MAX_MAP_ENTITIES];

int			nummiptex = 0;
char		miptex[MAX_MAP_TEXINFO][16];

//============================================================================

/*
===============
FindMiptex

===============
*/
int FindMiptex (char *name)
{
	int		i;

	for (i=0 ; i<nummiptex ; i++)
	{
		if (!strcmp (name, miptex[i]))
		return i;
	}
	if (nummiptex == MAX_MAP_TEXINFO)
		Error ("nummiptex == MAX_MAP_TEXINFO");
	strcpy (miptex[i], name);
	nummiptex++;
	return i;
}

/*
===============
FindTexinfo

Returns a global texinfo number
===============
*/
int	FindTexinfo (texinfo_t *t)
{
	int			i, j;
	texinfo_t	*tex;

	// set the special flag
	if (miptex[t->miptex][0] == '*' || !Q_strncasecmp (miptex[t->miptex], "sky",3) )
		t->flags |= TEX_SPECIAL;

	tex = texinfo;
	for (i=0 ; i<numtexinfo;i++, tex++)
	{
		if (t->miptex != tex->miptex)
			continue;
		if (t->flags != tex->flags)
			continue;

		for (j=0 ; j<8 ; j++)
			if (t->vecs[0][j] != tex->vecs[0][j])
				break;
		if (j != 8)
			continue;

		return i;
	}

	// allocate a new texture
	if (numtexinfo == MAX_MAP_TEXINFO)
		Error ("numtexinfo == MAX_MAP_TEXINFO");
	texinfo[i] = *t;
	numtexinfo++;

	return i;
}


//============================================================================

// LordHavoc: increased maximum token length from 128 to 1024
#define	MAXTOKEN	1024

char	token[MAXTOKEN];
qboolean	unget;
char	*script_p;
int		scriptline;

void	StartTokenParsing (char *data)
{
	scriptline = 1;
	script_p = data;
	unget = false;
}

qboolean GetToken (qboolean crossline)
{
	char    *token_p;

	if (unget)                         // is a token already waiting?
		return true;

	//
	// skip space
	//
	skipspace:
	while (*script_p <= 32)
	{
		if (!*script_p)
		{
			if (!crossline)
				Error ("Line %i is incomplete",scriptline);
			return false;
		}
		if (*script_p++ == '\n')
		{
			if (!crossline)
				Error ("Line %i is incomplete",scriptline);
			scriptline++;
		}
	}

	if (script_p[0] == '/' && script_p[1] == '/')	// comment field
	{
		if (!crossline)
			Error ("Line %i is incomplete\n",scriptline);
		while (*script_p++ != '\n')
			if (!*script_p)
			{
				if (!crossline)
					Error ("Line %i is incomplete",scriptline);
				return false;
			}
		goto skipspace;
	}

	//
	// copy token
	//
	token_p = token;

	if (*script_p == '"')
	{
		script_p++;
		while ( *script_p != '"' )
		{
			if (!*script_p)
				Error ("EOF inside quoted token");
			*token_p++ = *script_p++;
			if (token_p > &token[MAXTOKEN-1])
				Error ("Token too large on line %i",scriptline);
		}
		script_p++;
	}
	else while ( *script_p > 32 )
	{
		*token_p++ = *script_p++;
		if (token_p > &token[MAXTOKEN-1])
			Error ("Token too large on line %i",scriptline);
	}

	*token_p = 0;

	return true;
}

void UngetToken ()
{
	unget = true;
}


//============================================================================

entity_t	*mapent;

/*
=================
ParseEpair
=================
*/
void ParseEpair (void)
{
	epair_t	*e;

	e = malloc (sizeof(epair_t));
	memset (e, 0, sizeof(epair_t));
	e->next = mapent->epairs;
	mapent->epairs = e;

	if (strlen(token) >= MAX_KEY-1)
		Error ("ParseEpair: token too long");
	e->key = copystring(token);
	GetToken (false);
	if (strlen(token) >= MAX_VALUE-1)
		Error ("ParseEpair: token too long");
	e->value = copystring(token);
}

//============================================================================


/*
==================
textureAxisFromPlane
==================
*/
vec3_t	baseaxis[18] =
{
	{0,0,1}, {1,0,0}, {0,-1,0},			// floor
	{0,0,-1}, {1,0,0}, {0,-1,0},		// ceiling
	{1,0,0}, {0,1,0}, {0,0,-1},			// west wall
	{-1,0,0}, {0,1,0}, {0,0,-1},		// east wall
	{0,1,0}, {1,0,0}, {0,0,-1},			// south wall
	{0,-1,0}, {1,0,0}, {0,0,-1}			// north wall
};

void TextureAxisFromPlane(plane_t *pln, vec3_t xv, vec3_t yv)
{
	int		bestaxis;
	vec_t	dot,best;
	int		i;

	best = 0;
	bestaxis = 0;

	for (i=0 ; i<6 ; i++)
	{
		dot = DotProduct (pln->normal, baseaxis[i*3]);
		if (dot > best)
		{
			best = dot;
			bestaxis = i;
		}
	}

	VectorCopy (baseaxis[bestaxis*3+1], xv);
	VectorCopy (baseaxis[bestaxis*3+2], yv);
}


//=============================================================================


/*
=================
ParseBrush
=================
*/
void ParseBrush (void)
{
	int			i, j, sv, tv, hltexdef;
	vec_t		planepts[3][3], t1[3], t2[3], d, rotate, scale[2], vecs[2][4], ang, sinv, cosv, ns, nt;
	mbrush_t	*b;
	mface_t		*f, *f2;
	plane_t	plane;
	texinfo_t	tx;

	b = &mapbrushes[nummapbrushes];
	nummapbrushes++;
	b->next = mapent->brushes;
	mapent->brushes = b;

	do
	{
		if (!GetToken (true))
			break;
		if (!strcmp (token, "}") )
			break;

		// read the three point plane definition
		for (i = 0;i < 3;i++)
		{
			if (i != 0)
				GetToken (true);
			if (strcmp (token, "(") )
				Error ("parsing brush on line %d\n", scriptline);

			for (j = 0;j < 3;j++)
			{
				GetToken (false);
				planepts[i][j] = atof(token); // LordHavoc: float coords
			}

			GetToken (false);
			if (strcmp (token, ")") )
				Error ("parsing brush on line %d\n", scriptline);
		}

		//fflush(stdout);

		// convert points to a plane
		VectorSubtract(planepts[0], planepts[1], t1);
		VectorSubtract(planepts[2], planepts[1], t2);
		CrossProduct(t1, t2, plane.normal);
		VectorNormalize(plane.normal);
		plane.dist = DotProduct(planepts[1], plane.normal);

		// read the texturedef
		memset (&tx, 0, sizeof(tx));
		GetToken (false);
		tx.miptex = FindMiptex (token);
		GetToken (false);
		if ((hltexdef = !strcmp(token, "[")))
		{
			// S vector
			GetToken(false);
			vecs[0][0] = atof(token);
			GetToken(false);
			vecs[0][1] = atof(token);
			GetToken(false);
			vecs[0][2] = atof(token);
			GetToken(false);
			vecs[0][3] = atof(token);
			// ]
			GetToken(false);
			// [
			GetToken(false);
			// T vector
			GetToken(false);
			vecs[1][0] = atof(token);
			GetToken(false);
			vecs[1][1] = atof(token);
			GetToken(false);
			vecs[1][2] = atof(token);
			GetToken(false);
			vecs[1][3] = atof(token);
			// ]
			GetToken(false);
		}
		else
		{
			vecs[0][3] = atof(token); // LordHavoc: float coords
			GetToken (false);
			vecs[1][3] = atof(token); // LordHavoc: float coords
		}
		GetToken (false);
		rotate = atof(token);	 // LordHavoc: float coords
		GetToken (false);
		scale[0] = atof(token); // LordHavoc: was already float coords
		GetToken (false);
		scale[1] = atof(token); // LordHavoc: was already float coords

		// if the three points are all on a previous plane, it is a
		// duplicate plane
		for (f2 = b->faces ; f2 ; f2=f2->next)
		{
			for (i = 0;i < 3;i++)
			{
				d = DotProduct(planepts[i],f2->plane.normal) - f2->plane.dist;
				if (d < -ON_EPSILON || d > ON_EPSILON)
					break;
			}
			if (i==3)
				break;
		}
		if (f2)
		{
			printf ("WARNING: brush with duplicate plane (first point is at %g %g %g, .map file line number %d)\n", planepts[0][0], planepts[0][1], planepts[0][2], scriptline);
			continue;
		}

		if (DotProduct(plane.normal, plane.normal) < 0.1)
		{
			printf ("WARNING: brush plane with no normal on line %d\n", scriptline);
			continue;
		}

		/*
		// LordHavoc: fix for CheckFace: point off plane errors in some maps (most notably QOOLE ones),
		// and hopefully preventing most 'portal clipped away' warnings
		VectorNormalize (plane.normal);
		for (j = 0;j < 3;j++)
			plane.normal[j] = (Q_rint((vec_t) plane.normal[j] * (vec_t) 8.0)) * (vec_t) (1.0 / 8.0);
		VectorNormalize (plane.normal);
		plane.dist = DotProduct (t3, plane.normal);
		d = (Q_rint(plane.dist * 8.0)) * (1.0 / 8.0);
		//if (fabs(d - plane.dist) >= (0.4 / 8.0))
		//	printf("WARNING: correcting minor math errors in brushface on line %d\n", scriptline);
		plane.dist = d;
		*/

		/*
		VectorNormalize (plane.normal);
		plane.dist = DotProduct (t3, plane.normal);

		VectorCopy(plane.normal, v);
		//for (j = 0;j < 3;j++)
		//	v[j] = (Q_rint((vec_t) v[j] * (vec_t) 32.0)) * (vec_t) (1.0 / 32.0);
		VectorNormalize (v);
		d = (Q_rint(DotProduct (t3, v) * 8.0)) * (1.0 / 8.0);

		// if deviation is too high, warn  (frequently happens on QOOLE maps)
		if (fabs(DotProduct(v, plane.normal) - 1.0) > (0.5 / 32.0)
		 || fabs(d - plane.dist) >= (0.25 / 8.0))
			printf("WARNING: minor misalignment of brushface on line %d\n"
			       "normal     %f %f %f (l: %f d: %f)\n"
			       "rounded to %f %f %f (l: %f d: %f r: %f)\n",
			       scriptline,
			       (vec_t) plane.normal[0], (vec_t) plane.normal[1], (vec_t) plane.normal[2], (vec_t) sqrt(DotProduct(plane.normal, plane.normal)), (vec_t) DotProduct (t3, plane.normal),
			       (vec_t) v[0], (vec_t) v[1], (vec_t) v[2], (vec_t) sqrt(DotProduct(v, v)), (vec_t) DotProduct(t3, v), (vec_t) d);
		//VectorCopy(v, plane.normal);
		//plane.dist = d;
		*/

		if (!hltexdef)
		{
			// fake proper texture vectors from QuakeEd style
			TextureAxisFromPlane(&plane, vecs[0], vecs[1]);
		}

		// rotate axis
		     if (rotate ==  0) {sinv = 0;cosv = 1;}
		else if (rotate == 90) {sinv = 1;cosv = 0;}
		else if (rotate == 180) {sinv = 0;cosv = -1;}
		else if (rotate == 270) {sinv = -1;cosv = 0;}
		else {ang = rotate * (Q_PI / 180);sinv = sin(ang);cosv = cos(ang);}

		// LordHavoc: I don't quite understand this
		for (sv = 0;sv < 2 && !vecs[0][sv];sv++);
		for (tv = 0;tv < 2 && !vecs[1][tv];tv++);

		for (i = 0;i < 2;i++)
		{
			// rotate
			ns = cosv * vecs[i][sv] - sinv * vecs[i][tv];
			nt = sinv * vecs[i][sv] +  cosv * vecs[i][tv];
			vecs[i][sv] = ns;
			vecs[i][tv] = nt;
			// scale and store into texinfo
			d = 1.0 / (scale[i] ? scale[i] : 1.0);
			for (j = 0;j < 3;j++)
				tx.vecs[i][j] = vecs[i][j] * d;
			tx.vecs[i][3] = vecs[i][3];
		}

		f = malloc(sizeof(mface_t));
		f->next = b->faces;
		b->faces = f;
		f->plane = plane;
		f->texinfo = FindTexinfo (&tx);
		nummapbrushfaces++;
	}
	while (1);
}

/*
================
ParseEntity
================
*/
qboolean	ParseEntity (void)
{
	if (!GetToken (true))
		return false;

	if (strcmp (token, "{") )
		Error ("ParseEntity: { not found");

	if (num_entities == MAX_MAP_ENTITIES)
		Error ("num_entities == MAX_MAP_ENTITIES");

	mapent = &entities[num_entities];
	num_entities++;

	do
	{
		fflush(stdout);
		if (!GetToken (true))
			Error ("ParseEntity: EOF without closing brace");
		if (!strcmp (token, "}") )
			break;
		if (!strcmp (token, "{") )
			ParseBrush ();
		else
			ParseEpair ();
	}
	while (1);

	GetVectorForKey (mapent, "origin", mapent->origin);
	return true;
}

/*
================
LoadMapFile
================
*/
void LoadMapFile (char *filename)
{
	void	*buf;

	LoadFile (filename, &buf);

	StartTokenParsing (buf);

	num_entities = 0;

	while (ParseEntity ());

	free (buf);

	qprintf ("--- LoadMapFile ---\n");
	qprintf ("%s\n", filename);
	qprintf ("%5i faces\n", nummapbrushfaces);
	qprintf ("%5i brushes\n", nummapbrushes);
	qprintf ("%5i entities\n", num_entities);
	qprintf ("%5i textures\n", nummiptex);
	qprintf ("%5i texinfo\n", numtexinfo);
}

void PrintEntity (entity_t *ent)
{
	epair_t	*ep;

	for (ep=ent->epairs ; ep ; ep=ep->next)
		printf ("%20s : %s\n", ep->key, ep->value);
}


char 	*ValueForKey (entity_t *ent, char *key)
{
  epair_t	*ep;

  for (ep=ent->epairs ; ep ; ep=ep->next)
    if (!strcmp (ep->key, key) )
      return ep->value;
  return "";
}

void 	SetKeyValue (entity_t *ent, char *key, char *value)
{
	epair_t	*ep;

	for (ep=ent->epairs ; ep ; ep=ep->next)
		if (!strcmp (ep->key, key) )
		{
			free (ep->value);
			ep->value = copystring(value);
			return;
		}
	ep = malloc (sizeof(*ep));
	ep->next = ent->epairs;
	ent->epairs = ep;
	ep->key = copystring(key);
	ep->value = copystring(value);
}


void 	GetVectorForKey (entity_t *ent, char *key, vec3_t vec)
{
	char	*k;
	double	v1, v2, v3;

	k = ValueForKey (ent, key);
	v1 = v2 = v3 = 0;
	// scanf into doubles, then assign, so it is vec_t size independent
	sscanf (k, "%lf %lf %lf", &v1, &v2, &v3);
	vec[0] = v1;
	vec[1] = v2;
	vec[2] = v3;
}


void WriteEntitiesToString (void)
{
	char	*buf, *end;
	epair_t	*ep;
	char	line[16384];
	int		i;

	buf = dentdata;
	end = buf;
	*end = 0;

	for (i=0 ; i<num_entities ; i++)
	{
		ep = entities[i].epairs;
		if (!ep)
			continue;	// ent got removed

		strcat (end,"{\n");
		end += 2;

		for (ep = entities[i].epairs ; ep ; ep=ep->next)
		{
			sprintf (line, "\"%s\" \"%s\"\n", ep->key, ep->value);
			strcat (end, line);
			end += strlen(line);
		}
		strcat (end,"}\n");
		end += 2;

		if (end > buf + MAX_MAP_ENTSTRING)
			Error ("Entity text too long");
	}
	entdatasize = end - buf + 1;
}

