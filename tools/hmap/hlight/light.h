
#include "cmdlib.h"
#include "mathlib.h"
#include "bspfile.h"
#include "entities.h"
//#include "threads.h"

#define ON_EPSILON 0.1

#define MAXLIGHTS 1024
#define LIGHTDISTBIAS 65536.0

extern char lightsfilename[1024];

void LoadNodes (char *file);
qboolean TestLine (vec3_t start, vec3_t stop);

typedef struct lightchain_s
{
	entity_t *light;
	struct lightchain_s *next;
}
lightchain_t;

void LightFace (dface_t *f, lightchain_t *lightchain, entity_t **novislight, int novislights, vec3_t faceorg);
void LightLeaf (dleaf_t *leaf);

void MakeTnodes (dmodel_t *bm);

extern	int		c_culldistplane, c_proper;

void TransformSample (vec3_t in, vec3_t out);
void RotateSample (vec3_t in, vec3_t out);

extern qboolean relight;

extern int extrasamplesbit; // power of 2 extra sampling (0 = 1x1 sampling, 1 = 2x2 sampling, 2 = 4x4 sampling, etc)
extern vec_t extrasamplesscale; // 1.0 / pointspersample (extrasamples related)
extern vec_t globallightscale;
