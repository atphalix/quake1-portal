
#define DEFAULTLIGHTLEVEL	300
#define DEFAULTFALLOFF	1.0f

typedef struct epair_s
{
	struct epair_s *next;
	char key[MAX_KEY];
	char value[MAX_VALUE];
} epair_t;

typedef struct entity_s
{
	char classname[64];
	vec3_t origin;
	vec_t angle;
	int light;
	// LordHavoc: added falloff (smaller fractions = bigger light area), color, and lightradius (also subbrightness to implement lightradius)
	vec_t falloff;
	vec_t lightradius;
	vec_t subbrightness;
	vec_t lightoffset;
	vec3_t color;
	vec3_t spotdir;
	vec_t spotcone;
	unsigned short visbyte, visbit; // which byte and bit to look at in the visdata for the leaf this light is in
	int style;
	char target[32];
	char targetname[32];
	struct epair_s *epairs;
	struct entity_s *targetent;
} entity_t;

extern entity_t entities[MAX_MAP_ENTITIES];
extern int num_entities;

char *ValueForKey (entity_t *ent, char *key);
void SetKeyValue (entity_t *ent, char *key, char *value);
entity_t *FindEntityWithKeyPair( char *key, char *value );
void GetVectorForKey (entity_t *ent, char *key, vec3_t vec);

void LoadEntities (void);
void WriteEntitiesToString (void);
