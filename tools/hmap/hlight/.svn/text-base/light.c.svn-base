// lighting.c

#include "light.h"

/*

NOTES
-----

*/

dmodel_t	*bspmodel;

qboolean	lightvis;
qboolean	relight;

int			extrasamplesbit; // power of 2 extra sampling (0 = 1x1 sampling, 1 = 2x2 sampling, 2 = 4x4 sampling, etc)
vec_t		extrasamplesscale; // 1.0 / pointspersample (extrasamples related)
vec_t		globallightscale;

// filename to write light list to
char lightsfilename[1024];

byte currentvis[(MAX_MAP_LEAFS + 7) / 8];

void DecompressVis(byte *in, byte *out, int size)
{
	byte *end = out + size;
	int n;
	while (out < end)
	{
		n = *in++;
		if (n)
			*out++ = n;
		else
		{
			n = *in++;
			while (n--)
				*out++ = 0;
		}
	}
}

dleaf_t *Light_PointInLeaf(vec3_t point)
{
	int num;
	num = 0;
	while (num >= 0)
		num = dnodes[num].children[DotProduct(point, dplanes[dnodes[num].planenum].normal) < dplanes[dnodes[num].planenum].dist];
	return dleafs + (-1 - num);
}

#define LIGHTCHAINS (MAX_MAP_FACES * 32)

lightchain_t *surfacelightchain[MAX_MAP_FACES];
lightchain_t lightchainbuf[LIGHTCHAINS];
byte surfacehit[MAX_MAP_FACES];
entity_t *novislight[MAX_MAP_ENTITIES];
entity_t *alllight[MAX_MAP_ENTITIES];
int novislights, alllights;
int lightchainbufindex;

/*
=============
LightWorld
=============
*/
extern int dlightdatapos;
void LightWorld (void)
{
	int			i, k, n, m, count;
	unsigned short	*mark;
	time_t		lightstarttime, oldtime, newtime;
	entity_t	*entity;
	dleaf_t		*leaf;
	int			lightcount = 0, castcount = 0, emptycount = 0, solidcount = 0, watercount = 0, slimecount = 0, lavacount = 0, skycount = 0, misccount = 0, ignorevis;
	vec3_t		org;
	char		name[8];
	entity_t	*ent;
//	filebase = file_p = dlightdata;
//	file_end = filebase + MAX_MAP_LIGHTING;
	if (!relight)
		lightdatasize = 0;
	rgblightdatasize = 0;
	lightstarttime = time(NULL);

	lightchainbufindex = 0;
	novislights = alllights = 0;
	memset(surfacelightchain, 0, sizeof(surfacelightchain));

	// LordHavoc: find the right leaf for each entity
	for (i = 0, entity = entities;i < num_entities;i++, entity++)
	{
		if (!entity->light)
			continue;
		lightcount++;
		alllight[alllights++] = entity;
		leaf = Light_PointInLeaf(entity->origin);
		ignorevis = false;
		switch (leaf->contents)
		{
		case CONTENTS_EMPTY:
			emptycount++;
			break;
		case CONTENTS_SOLID:
			solidcount++;
			ignorevis = true;
			break;
		case CONTENTS_WATER:
			watercount++;
			break;
		case CONTENTS_SLIME:
			slimecount++;
			break;
		case CONTENTS_LAVA:
			lavacount++;
			break;
		case CONTENTS_SKY:
			skycount++;
			ignorevis = true;
			break;
		default:
			misccount++;
			break;
		}
		if (leaf->visofs == -1 || ignorevis || (!lightvis))
		{
			/*
			if ((lightchainbufindex + numfaces) > LIGHTCHAINS)
				Error("LightWorld: ran out of light chains!  complain to maintainer of hlight\n");
			for (m = 0;m < numfaces;m++)
			{
				castcount++;
				lightchainbuf[lightchainbufindex].light = entity;
				lightchainbuf[lightchainbufindex].next = surfacelightchain[m];
				surfacelightchain[m] = &lightchainbuf[lightchainbufindex++];
			}
			*/
			castcount += numfaces;
			novislight[novislights++] = entity;
		}
		else
		{
			DecompressVis(dvisdata + leaf->visofs, currentvis, (numleafs + 7) >> 3);
			memset(surfacehit, 0, numfaces);
			for (n = 0, leaf = dleafs+1;n < numleafs;n++, leaf++) // leafs begin at 1
			{
				if (!leaf->nummarksurfaces)
					continue;
				if (currentvis[n >> 3] & (1 << (n & 7)))
				{
					if ((lightchainbufindex + leaf->nummarksurfaces) > LIGHTCHAINS)
						Error("LightWorld: ran out of light chains!  complain to maintainer of hlight\n");
					for (m = 0, mark = dmarksurfaces + leaf->firstmarksurface;m < leaf->nummarksurfaces;m++, mark++)
					{
						if (surfacehit[*mark])
							continue;
						surfacehit[*mark] = true;
						castcount++;
						lightchainbuf[lightchainbufindex].light = entity;
						lightchainbuf[lightchainbufindex].next = surfacelightchain[*mark];
						surfacelightchain[*mark] = &lightchainbuf[lightchainbufindex++];
					}
				}
			}
		}
	}

	printf("%4i lights, %4i air, %4i solid, %4i water, %4i slime, %4i lava, %4i sky, %4i unknown\n", lightcount, emptycount, solidcount, watercount, slimecount, lavacount, skycount, misccount);

	i = 0;
	for (m = 0;m < numfaces;m++)
		if (surfacelightchain[m])
			i++;
	printf("%5i faces, %5i (%3i%%) may receive light\n", numfaces, i, i * 100 / numfaces);

	if (solidcount || skycount)
		printf("warning: %4i lights of %4i lights (%3i%%) were found in sky or solid and will not be accelerated using vis, move them out of the solid or sky to accelerate compiling\n", solidcount+skycount, lightcount, (solidcount+skycount) * 100 / lightcount);

	printf("%4i lights will be cast onto %5i surfaces, %10i casts will be performed\n", lightcount, numfaces, castcount);

	// LordHavoc: let there be light
	count = dmodels[0].numfaces;
//	k = 1;
//	j = (int) ((double) count * (double) k * (1.0 / 100.0));
	org[0] = org[1] = org[2] = 0;
	oldtime = time(NULL);
	for (m = 0;m < count;)
	{
		LightFace (dfaces + m + dmodels[0].firstface, surfacelightchain[m + dmodels[0].firstface], novislight, novislights, org);
		m++;
		newtime = time(NULL);
		if (newtime != oldtime)
		{
			printf ("\rworld face %5i of %5i (%3i%%), estimated time left: %5i ", m, count, (int) (m*100)/count, (int) (((count-m)*(newtime-lightstarttime))/m));
			fflush(stdout);
			oldtime = newtime;
		}
	}
	printf ("\n%5i faces done\nlightdatasize: %i\n", numfaces, lightdatasize);

	printf("\nlighting %5i submodels:\n", nummodels);
	fflush(stdout);
	// LordHavoc: light bmodels
	for (k = 1;k < nummodels;k++)
	{
		newtime = time(NULL);
		if (newtime != oldtime)
		{
			m = k;
			count = nummodels;
			printf ("\rsubmodel %3i of %3i (%3i%%), estimated time left: %5i ", m, count, (int) (m*100)/count, (int) (((count-m)*(newtime-lightstarttime))/m));
			fflush(stdout);
			oldtime = newtime;
		}
		sprintf(name, "*%d", k);
		ent = FindEntityWithKeyPair("model", name);
		if (!ent)
			Error("FindFaceOffsets: Couldn't find entity for model %s.\n", name);

		org[0] = org[1] = org[2] = 0;
		if (!strncmp(ValueForKey (ent, "classname"), "rotate_", 7))
			GetVectorForKey(ent, "origin", org);

		for (m = 0;m < dmodels[k].numfaces;m++)
			LightFace (dfaces + m + dmodels[k].firstface, NULL, alllight, alllights, org);
	}

//	lightdatasize = file_p - filebase;
//	rgblightdatasize = lightdatasize * 3;

	printf ("\n%5i submodels done\nlightdatasize: %i\n", nummodels, lightdatasize);
}

void CheckLightmaps(void);

/*
========
main

light modelfile
========
*/
int main (int argc, char **argv)
{
	char source[1024];
	double start, end;
	int i;

// LordHavoc
	printf ("hlight 1.04 by LordHavoc\n");
	printf ("based on id Software's quake light utility source code\n");
	extrasamplesbit = 0;
	lightvis = true;
	relight = false;
	globallightscale = 1.0;

	for (i=1 ; i<argc ; i++)
	{
		if (!strcmp(argv[i],"-extra"))
		{
			extrasamplesbit = 1;
			printf ("2x2 sampling enabled (tip: -extra4x4 is even higher quality)\n");
		}
		else if (!strcmp(argv[i],"-extra4x4"))
		{
			extrasamplesbit = 2;
			printf ("4x4 sampling enabled\n");
		}
		else if (!strcmp(argv[i],"-nolightvis"))
		{
			printf("use of vis data to optimize lighting disabled\n");
			lightvis = false;
		}
		else if (!strcmp(argv[i],"-relight"))
		{
			printf("relighting map to create .lit file without modifying .bsp\n");
			relight = true;
		}
		else if (!strcmp(argv[i],"-intensity"))
		{
			i++;
			if (i >= argc)
				Error("no value was given to -intensity\n");
			globallightscale = atof(argv[i]);
			if (globallightscale < 0.01)
				globallightscale = 0.01;
		}
		else if (argv[i][0] == '-')
			Error ("Unknown option \"%s\"", argv[i]);
		else
			break;
	}

	extrasamplesscale = 1.0f / (1 << (extrasamplesbit * 2));

// LordHavoc
	if (i != argc - 1)
		Error ("%s",
"usage: hlight [options] bspfile\n"
"Quick usage notes for entities: (place these in key/value pairs)\n"
"wait - falloff rate (1.0 default, 0.5 = bigger radius, 2 = smaller, affects area the light covers)\n"
"_color - 3 values (red green blue), specifies color of light, the scale of the numbers does not matter (\"1 3 2.5\" is identical to \"1000 3000 2500\")\n"
"_lightradius - limits light to this radius (and darkens light to make it blend well at the edges)\n"
"What the options do:\n"
"-extra         antialiased lighting (takes much longer, higher quality)\n"
"-extra4x4      antialiased lighting (even slower and higher quality than -extra)\n"
"-nolightvis    disables use of visibility data to optimize lighting\n"
"-relight       makes a .lit file for an existing map without modifying the .bsp\n"
		);

	printf ("----- LightFaces ----\n");

//	InitThreads ();

	start = I_DoubleTime ();

	strcpy(source, argv[i]);
	strcpy(litfilename, source);
	strcpy(lightsfilename, source);
	DefaultExtension(source, ".bsp");
	ReplaceExtension(litfilename, ".lit");
	ReplaceExtension(lightsfilename, ".lights");

	LoadBSPFile (source);
	memset(dlightdata, 0, sizeof(dlightdata));
	memset(drgblightdata, 0, sizeof(drgblightdata));
	//for (i = 0;i < sizeof(dlightdata);i++)
	//	dlightdata[i] = i;
	CheckLightmaps();

	if (!visdatasize)
	{
		printf("no visibility data found (run hvis before hlight to compile faster)\n");
		lightvis = false;
	}

	LoadEntities ();
	CheckLightmaps();

	MakeTnodes (&dmodels[0]);
	CheckLightmaps();

	LightWorld ();
	CheckLightmaps();

	WriteEntitiesToString ();
	CheckLightmaps();
	WriteBSPFile (source, relight);
	CheckLightmaps();

	end = I_DoubleTime ();
	printf ("%5.1f seconds elapsed\n", end-start);

#if _MSC_VER && _DEBUG
	printf("press any key\n");
	getchar();
#endif

	return 0;
}

