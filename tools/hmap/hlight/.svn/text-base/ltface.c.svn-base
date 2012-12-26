
#include "light.h"

/*
===============================================================================

SAMPLE POINT DETERMINATION

void SetupBlock (dface_t *f) Returns with point[] set

This is a little tricky because the lightmap covers more area than the face.
If done in the straightforward fashion, some of the
sample points will be inside walls or on the other side of walls, causing
false shadows and light bleeds.

To solve this, I only consider a sample point valid if a line can be drawn
between it and the exact midpoint of the face.  If invalid, it is adjusted
towards the center until it is valid.

(this doesn't completely work)

===============================================================================
*/

// LordHavoc: increased from 18x18 samples to 256x256 samples
#define SINGLEMAP (256*256)

typedef struct
{
	vec3_t v;
	int samplepos; // the offset into the lightmap that this point contributes to
}
lightpoint_t;

typedef struct
{
	vec3_t c;
}
lightsample_t;

typedef struct
{
	vec_t			facedist;
	vec3_t			facenormal;

	int				numpoints;
	int				numsamples;
	// *16 for -extra4x4
	lightpoint_t	point[SINGLEMAP*16];
	lightsample_t	sample[MAXLIGHTMAPS][SINGLEMAP];

	vec3_t			texorg;
	vec3_t			worldtotex[2];	// s = (world - texorg) . worldtotex[0]
	vec3_t			textoworld[2];	// world = texorg + s * textoworld[0]

	vec_t			exactmins[2], exactmaxs[2];

	int				texmins[2], texsize[2];
	int				lightstyles[MAXLIGHTMAPS];
	dface_t			*face;
}
lightinfo_t;



/*
================
CalcFaceVectors

Fills in texorg, worldtotex. and textoworld
================
*/
void CalcFaceVectors (lightinfo_t *l, vec3_t faceorg)
{
	texinfo_t	*tex;
	int			i, j;
	vec3_t	texnormal;
	vec_t	distscale;
	vec_t	dist, len;

	tex = &texinfo[l->face->texinfo];

// convert from float to vec_t
	for (i=0 ; i<2 ; i++)
		for (j=0 ; j<3 ; j++)
			l->worldtotex[i][j] = tex->vecs[i][j];

// calculate a normal to the texture axis.  points can be moved along this
// without changing their S/T
	// LordHavoc: this is actually a CrossProduct
	texnormal[0] = tex->vecs[1][1]*tex->vecs[0][2] - tex->vecs[1][2]*tex->vecs[0][1];
	texnormal[1] = tex->vecs[1][2]*tex->vecs[0][0] - tex->vecs[1][0]*tex->vecs[0][2];
	texnormal[2] = tex->vecs[1][0]*tex->vecs[0][1] - tex->vecs[1][1]*tex->vecs[0][0];
	VectorNormalize (texnormal);

// flip it towards plane normal
	distscale = DotProduct (texnormal, l->facenormal);
	if (!distscale)
		Error ("Texture axis perpendicular to face");
	if (distscale < 0)
	{
		distscale = -distscale;
		VectorNegate (texnormal, texnormal);
	}

// distscale is the ratio of the distance along the texture normal to
// the distance along the plane normal
	distscale = 1/distscale;

	for (i=0 ; i<2 ; i++)
	{
		len = VectorLength (l->worldtotex[i]);
		dist = DotProduct (l->worldtotex[i], l->facenormal);
		dist *= distscale;
		VectorMA (l->worldtotex[i], -dist, texnormal, l->textoworld[i]);
		VectorScale (l->textoworld[i], (1/len)*(1/len), l->textoworld[i]);
	}


// calculate texorg on the texture plane
	for (i=0 ; i<3 ; i++)
		l->texorg[i] = -tex->vecs[0][3] * l->textoworld[0][i] - tex->vecs[1][3] * l->textoworld[1][i];

	VectorAdd(l->texorg, faceorg, l->texorg);

// project back to the face plane
	dist = DotProduct (l->texorg, l->facenormal) - l->facedist - 1;
	dist *= distscale;
	VectorMA (l->texorg, -dist, texnormal, l->texorg);

}

/*
================
CalcFaceExtents

Fills in s->texmins[] and s->texsize[]
also sets exactmins[] and exactmaxs[]
================
*/
void CalcFaceExtents (lightinfo_t *l)
{
	dface_t *s;
	vec_t	mins[2], maxs[2], val;
	int		i,j, e;
	dvertex_t	*v;
	texinfo_t	*tex;

	s = l->face;

	mins[0] = mins[1] = BOGUS_RANGE;
	maxs[0] = maxs[1] = -BOGUS_RANGE;

	tex = &texinfo[s->texinfo];

	for (i=0 ; i<s->numedges ; i++)
	{
		e = dsurfedges[s->firstedge+i];
		if (e >= 0)
			v = dvertexes + dedges[e].v[0];
		else
			v = dvertexes + dedges[-e].v[1];

		for (j=0 ; j<2 ; j++)
		{
			val = v->point[0] * tex->vecs[j][0] +
				v->point[1] * tex->vecs[j][1] +
				v->point[2] * tex->vecs[j][2] +
				tex->vecs[j][3];
			if (val < mins[j])
				mins[j] = val;
			if (val > maxs[j])
				maxs[j] = val;
		}
	}

	for (i=0 ; i<2 ; i++)
	{
		l->exactmins[i] = mins[i];
		l->exactmaxs[i] = maxs[i];

		mins[i] = floor(mins[i]/16);
		maxs[i] = ceil(maxs[i]/16);

		l->texmins[i] = mins[i];
		l->texsize[i] = maxs[i] + 1 - mins[i];
		if (l->texsize[i] > 256) // LordHavoc: was 17, much much bigger allowed now
			Error ("Bad surface extents");
	}
}

void CalcSamples (lightinfo_t *l)
{
	/*
	int				i, mapnum;
	lightsample_t	*sample;
	*/

	l->numsamples = l->texsize[0] * l->texsize[1];
	// no need to clear because the lightinfo struct was cleared already
	/*
	for (mapnum = 0;mapnum < MAXLIGHTMAPS;mapnum++)
	{
		for (i = 0, sample = l->sample[mapnum];i < l->numsamples;i++, sample++)
		{
			sample->c[0] = 0;
			sample->c[1] = 0;
			sample->c[2] = 0;
		}
	}
	*/
}

/*
=================
CalcPoints

For each texture aligned grid point, back project onto the plane
to get the world xyz value of the sample point
=================
*/
//int c_bad;
extern vec3_t testlineimpact;
void CalcPoints (lightinfo_t *l)
{
	int j, s, t, w, h, realw, realh, stepbit;
	vec_t starts, startt, us, ut, mids, midt;
	vec3_t facemid;
#if 1
	vec3_t			v;
#else
	int i;
#endif
	lightpoint_t	*point;

//
// fill in point array
// the points are biased towards the center of the surface
// to help avoid edge cases just inside walls
//
	mids = (l->exactmaxs[0] + l->exactmins[0])/2;
	midt = (l->exactmaxs[1] + l->exactmins[1])/2;

	for (j = 0;j < 3;j++)
		facemid[j] = l->texorg[j] + l->textoworld[0][j]*mids + l->textoworld[1][j]*midt;

	realw = l->texsize[0];
	realh = l->texsize[1];
	starts = l->texmins[0] * 16;
	startt = l->texmins[1] * 16;

	stepbit = 4 - extrasamplesbit;

	w = realw << extrasamplesbit;
	h = realh << extrasamplesbit;

	if (stepbit < 4)
	{
		starts -= 1 << stepbit;
		startt -= 1 << stepbit;
	}

	point = l->point;
	l->numpoints = w * h;
	for (t = 0;t < h;t++)
	{
		for (s = 0;s < w;s++, point++)
		{
			us = starts + (s << stepbit);
			ut = startt + (t << stepbit);
			point->samplepos = (t >> extrasamplesbit) * realw + (s >> extrasamplesbit);

#if 1
			// calculate texture point
			for (j = 0;j < 3;j++)
				point->v[j] = l->texorg[j] + l->textoworld[0][j] * us + l->textoworld[1][j] * ut;

			if (!TestLine (facemid, point->v))
			{
				// test failed, adjust to nearest position
				VectorCopy(testlineimpact, point->v);
				VectorSubtract(facemid, point->v, v);
				VectorNormalize(v);
				VectorMA(point->v, 0.25, v, point->v);
			}

			//VectorSubtract(facemid, point->v, v);
			//VectorNormalize(v);
			//VectorMA(point->v, 0.25, v, point->v);

#else
			// if a line can be traced from point to facemid, the point is good
			for (i = 0;i < 6;i++)
			{
				// calculate texture point
				for (j = 0;j < 3;j++)
					point->v[j] = l->texorg[j] + l->textoworld[0][j] * us + l->textoworld[1][j] * ut;

				if (TestLine (facemid, point->v))
					break;	// got it

				if (i & 1)
				{
					if (us > mids)
					{
						us -= 8;
						if (us < mids)
							us = mids;
					}
					else
					{
						us += 8;
						if (us > mids)
							us = mids;
					}
				}
				else
				{
					if (ut > midt)
					{
						ut -= 8;
						if (ut < midt)
							ut = midt;
					}
					else
					{
						ut += 8;
						if (ut > midt)
							ut = midt;
					}
				}
			}
			//if (i == 2)
			//	c_bad++;
#endif
		}
	}
}


/*
===============================================================================

FACE LIGHTING

===============================================================================
*/

int		c_culldistplane, c_proper;

/*
================
SingleLightFace
================
*/
void SingleLightFace (entity_t *light, lightinfo_t *l)
{
	vec_t			dist, idist;
	//vec_t			lightbrightness;
	vec_t			lightsubtract;
	vec_t			lightfalloff;
	vec3_t			incoming;
	vec_t			add;
	qboolean		hit;
	int				mapnum;
	int				i;
	vec3_t			spotvec;
	vec_t			spotcone;
	lightpoint_t	*point;
	lightsample_t	*sample;

	dist = (DotProduct (light->origin, l->facenormal) - l->facedist);

// don't bother with lights behind the surface
	if (dist < -0.25)
		return;

	//lightbrightness = light->light * 16384.0;
	lightfalloff = light->falloff;
	lightsubtract = light->subbrightness;
// don't bother with light too far away
	if (lightsubtract > (1.0 / (dist * dist * lightfalloff + LIGHTDISTBIAS)))
	{
		c_culldistplane++;
		return;
	}

	for (mapnum = 0;mapnum < MAXLIGHTMAPS;mapnum++)
	{
		if (l->lightstyles[mapnum] == light->style)
			break;
		if (l->lightstyles[mapnum] == 255)
		{
			if (relight)
				return;
			memset(l->sample[mapnum], 0, sizeof(lightsample_t) * l->numsamples);
			break;
		}
	}

	if (mapnum == MAXLIGHTMAPS)
	{
		printf ("WARNING: Too many light styles on a face\n");
		return;
	}

	spotcone = light->spotcone;
	VectorCopy(light->spotdir, spotvec);

//
// check it for real
//
	hit = relight; // if relighting, the style is already considered used
	c_proper++;

	for (i = 0, point = l->point;i < l->numpoints;i++, point++)
	{
		VectorSubtract (light->origin, point->v, incoming);
		dist = sqrt(DotProduct(incoming, incoming));
		idist = 1.0 / dist;
		incoming[0] *= idist;
		incoming[1] *= idist;
		incoming[2] *= idist;
		// spotlight
		if (spotcone > 0 && DotProduct (spotvec, incoming) > spotcone)
			continue;

		// LordHavoc: changed to be more realistic (entirely different lighting model)
		//// LordHavoc: FIXME: use subbrightness on all lights, simply to have some distance culling
		add = 1.0 / (dist * dist * lightfalloff + LIGHTDISTBIAS) - lightsubtract; // LordHavoc: added subbrightness
		if (add <= 0)
			continue;

		if (!TestLine(point->v, light->origin))
			continue;

		// LordHavoc: FIXME: decide this 0.5 bias based on shader properties (some are dull, some are shiny)
		add *= (DotProduct (incoming, l->facenormal) * 0.5 + 0.5);
		add *= extrasamplesscale;
		sample = &l->sample[mapnum][point->samplepos];
		sample->c[0] += add * light->color[0];
		sample->c[1] += add * light->color[1];
		sample->c[2] += add * light->color[2];
		// ignore real tiny lights
		if (!hit && ((sample->c[0]+sample->c[1]+sample->c[2]) >= 1))
			hit = true;
	}

	// if the style has some data now, make sure it is in the list
	if (hit)
		l->lightstyles[mapnum] = light->style;
}

/*
============
FixMinlight
============
*/
/*
void FixMinlight (lightinfo_t *l)
{
	int				i, j;
	lightsample_t	*sample;

// if minlight is set, there must be a style 0 light map
	if (!minlight)
		return;

	for (i = 0;i < l->numlightstyles;i++)
	{
		if (l->lightstyles[i] == 0)
		{
			for (j = 0, sample = l->sample[i];j < l->numsamples;j++, sample++)
			{
				if (sample->c[0] < minlight)
					sample->c[0] = minlight;
				if (sample->c[1] < minlight)
					sample->c[1] = minlight;
				if (sample->c[2] < minlight)
					sample->c[2] = minlight;
			}
			return;
		}
	}

	if (l->numlightstyles == MAXLIGHTMAPS)
		return;		// oh well..
	for (j = 0, sample = l->sample[i];j < l->numsamples;j++, sample++)
	{
		sample->c[0] = minlight;
		sample->c[1] = minlight;
		sample->c[2] = minlight;
	}
	l->lightstyles[i] = 0;
	l->numlightstyles++;
}
*/

int ranout = false;

/*
============
LightFace
============
*/
lightinfo_t l; // if this is made multithreaded again, this should be inside the function, but be warned, it's currently 38mb
void LightFace (dface_t *f, lightchain_t *lightchain, entity_t **novislight, int novislights, vec3_t faceorg)
{
	int				i, j, size;
	int				red, green, blue, white;
	byte			*out, *lit;
	lightsample_t	*sample;

	//memset (&l, 0, sizeof(l));
	l.face = f;

//
// some surfaces don't need lightmaps
//

	if (relight)
	{
		if (f->lightofs == -1)
			return;
	}
	else
	{
		for (i = 0;i < MAXLIGHTMAPS;i++)
			f->styles[i] = l.lightstyles[i] = 255;
		f->lightofs = -1;

		if (texinfo[f->texinfo].flags & TEX_SPECIAL)
		{
			// non-lit texture
			return;
		}
	}

//
// rotate plane
//
	VectorCopy (dplanes[f->planenum].normal, l.facenormal);
	l.facedist = dplanes[f->planenum].dist;
	if (f->side)
	{
		VectorNegate (l.facenormal, l.facenormal);
		l.facedist = -l.facedist;
	}

	CalcFaceVectors (&l, faceorg);
	CalcFaceExtents (&l);
	CalcSamples (&l);
	CalcPoints (&l);

	if (l.numsamples > SINGLEMAP)
		Error ("Bad lightmap size");

	if (relight)
	{
		// reserve the correct light styles
		for (i = 0;i < MAXLIGHTMAPS;i++)
		{
			l.lightstyles[i] = f->styles[i];
			if (l.lightstyles[i] != 255)
				memset(l.sample[i], 0, sizeof(lightsample_t) * l.numsamples);
		}
	}

//
// cast all lights
//
	while (lightchain)
	{
		SingleLightFace (lightchain->light, &l);
		lightchain = lightchain->next;
	}
	while (novislights--)
		SingleLightFace (*novislight++, &l);

	//FixMinlight (&l);

// save out the values

	if (relight)
	{
		// relighting an existing map without changing it's lightofs table

		for (i = 0;i < MAXLIGHTMAPS;i++)
			if (f->styles[i] == 255)
				break;
		size = l.numsamples * i;

		if (f->lightofs < 0 || f->lightofs + size > lightdatasize)
			Error("LightFace: Error while trying to relight map: invalid lightofs value, %i must be >= 0 && < %i\n", f->lightofs, lightdatasize);
	}
	else
	{
		// creating lightofs table from scratch

		for (i = 0;i < MAXLIGHTMAPS;i++)
			if (l.lightstyles[i] == 255)
				break;
		size = l.numsamples * i;

		if (!size)
		{
			// no light styles
			return;
		}

		if (lightdatasize + size > MAX_MAP_LIGHTING)
		{
			//Error("LightFace: ran out of lightmap dataspace");
			if (!ranout)
				printf("LightFace: ran out of lightmap dataspace");
			ranout = true;
			return;
		}

		for (i = 0;i < MAXLIGHTMAPS;i++)
			f->styles[i] = l.lightstyles[i];

		f->lightofs = lightdatasize;
		lightdatasize += size;
	}

	rgblightdatasize = lightdatasize * 3;

	out = dlightdata + f->lightofs;
	lit = drgblightdata + f->lightofs * 3;

	for (i = 0;i < MAXLIGHTMAPS && f->styles[i] != 255;i++)
	{
		for (j = 0, sample = l.sample[i];j < l.numsamples;j++, sample++)
		{
			red   = (int) sample->c[0];
			green = (int) sample->c[1];
			blue  = (int) sample->c[2];
			white = (int) ((sample->c[0] + sample->c[1] + sample->c[2]) * (1.0 / 3.0));
			if (red > 255) red = 255;
			if (red < 0) red = 0;
			if (green > 255) green = 255;
			if (green < 0) green = 0;
			if (blue > 255) blue = 255;
			if (blue < 0) blue = 0;
			if (white > 255) white = 255;
			if (white < 0) white = 0;
			*lit++ = red;
			*lit++ = green;
			*lit++ = blue;
			*out++ = white;
		}
	}
}

