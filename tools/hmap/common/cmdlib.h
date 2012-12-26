// cmdlib.h

#ifndef __CMDLIB__
#define __CMDLIB__

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <ctype.h>
#include <time.h>
#include <stdarg.h>
//#include <unistd.h>

#ifndef __BYTEBOOL__
#define __BYTEBOOL__
typedef enum {false, true} qboolean;
typedef unsigned char byte;
#endif

// the dec offsetof macro doesn't work very well...
#define myoffsetof(type,identifier) ((size_t)&((type *)0)->identifier)


// set these before calling CheckParm
extern int myargc;
extern char **myargv;

extern char *Q_strupr (char *in);
extern char *Q_strlower (char *in);
extern int Q_strncasecmp (char *s1, char *s2, int n);
extern int Q_strcasecmp (char *s1, char *s2);
//extern void Q_getwd (char *out);

extern int Q_filelength (FILE *f);
extern int	FileTime (char *path);

extern void	Q_mkdir (char *path);

extern char qdir[1024];
extern char gamedir[1024];
//extern void SetQdirFromPath (char *path);
//extern char *ExpandPath (char *path);
//extern char *ExpandPathAndArchive (char *path);


extern double I_DoubleTime (void);

extern void Error (char *error, ...);
extern int CheckParm (char *check);

extern FILE *SafeOpenWrite (char *filename);
extern FILE *SafeOpenRead (char *filename);
extern void SafeRead (FILE *f, void *buffer, int count);
extern void SafeWrite (FILE *f, void *buffer, int count);

extern int LoadFile (char *filename, void **bufferptr);
extern void SaveFile (char *filename, void *buffer, int count);

extern void DefaultExtension (char *path, char *extension);
extern void DefaultPath (char *path, char *basepath);
extern void ReplaceExtension (char *path, char *extension);

extern void ExtractFilePath (char *path, char *dest);
extern void ExtractFileBase (char *path, char *dest);
extern void ExtractFileExtension (char *path, char *dest);

extern int ParseNum (char *str);

extern short BigShort (short l);
extern short LittleShort (short l);
extern int BigLong (int l);
extern int LittleLong (int l);
extern float BigFloat (float l);
extern float LittleFloat (float l);


extern char *COM_Parse (char *data);

extern char com_token[1024];
extern qboolean com_eof;

extern char *copystring(char *s);


extern void CRC_Init(unsigned short *crcvalue);
extern void CRC_ProcessByte(unsigned short *crcvalue, byte data);
extern unsigned short CRC_Value(unsigned short crcvalue);

extern void COM_CreatePath (char *path);
extern void COM_CopyFile (char *from, char *to);

extern qboolean archive;
extern char archivedir[1024];


#endif
