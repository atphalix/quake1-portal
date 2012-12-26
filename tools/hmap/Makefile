##### Win32 variables #####

WIN32_HQBSP_EXE=bin/hqbsp.exe
WIN32_HVIS_EXE=bin/hvis.exe
WIN32_HLIGHT_EXE=bin/hlight.exe
WIN32_HQBSP_EXE_BACKSLASH=bin\hqbsp.exe
WIN32_HVIS_EXE_BACKSLASH=bin\hvis.exe
WIN32_HLIGHT_EXE_BACKSLASH=bin\hlight.exe
WIN32_LDFLAGS=-lwinmm

##### Unix variables #####

UNIX_HQBSP_EXE=bin/hqbsp
UNIX_HVIS_EXE=bin/hvis
UNIX_HLIGHT_EXE=bin/hlight
UNIX_LDFLAGS=-lm

##### Common variables #####

COMMONOBJECTS= common/cmdlib.o common/mathlib.o common/bspfile.o
HQBSPOBJECTS= hqbsp/brush.o hqbsp/csg4.o hqbsp/map.o hqbsp/merge.o hqbsp/nodraw.o hqbsp/outside.o hqbsp/portals.o hqbsp/qbsp.o hqbsp/region.o hqbsp/surfaces.o hqbsp/solidbsp.o hqbsp/tjunc.o hqbsp/writebsp.o hqbsp/wad.o
HVISOBJECTS= hvis/flow.o hvis/soundpvs.o hvis/vis.o
HLIGHTOBJECTS= hlight/entities.o hlight/light.o hlight/ltface.o hlight/trace.o

CC=gcc
CFLAGS=-Wall -O2 -Icommon

ifdef windir
CMD_RM=del
else
CMD_RM=rm -f
endif

##### Commands #####

.PHONY: all mingw clean

all:
ifdef windir
	$(MAKE) HQBSP_EXE=$(WIN32_HQBSP_EXE) HVIS_EXE=$(WIN32_HVIS_EXE) HLIGHT_EXE=$(WIN32_HLIGHT_EXE) LDFLAGS="$(WIN32_LDFLAGS)" $(WIN32_HQBSP_EXE) $(WIN32_HVIS_EXE) $(WIN32_HLIGHT_EXE)
else
	$(MAKE) HQBSP_EXE=$(UNIX_HQBSP_EXE) HVIS_EXE=$(UNIX_HVIS_EXE) HLIGHT_EXE=$(UNIX_HLIGHT_EXE) LDFLAGS="$(UNIX_LDFLAGS)" $(UNIX_HQBSP_EXE) $(UNIX_HVIS_EXE) $(UNIX_HLIGHT_EXE)
endif

mingw:
	$(MAKE) HQBSP_EXE=$(WIN32_HQBSP_EXE) HVIS_EXE=$(WIN32_HVIS_EXE) HLIGHT_EXE=$(WIN32_HLIGHT_EXE) LDFLAGS="$(WIN32_LDFLAGS)" $(WIN32_HQBSP_EXE) $(WIN32_HVIS_EXE) $(WIN32_HLIGHT_EXE)

.c.o:
	$(CC) $(CFLAGS) -c $*.c -o $*.o

$(HQBSP_EXE): $(HQBSPOBJECTS) $(COMMONOBJECTS)
	$(CC) -o $@ $^ $(LDFLAGS)

$(HVIS_EXE): $(HVISOBJECTS) $(COMMONOBJECTS)
	$(CC) -o $@ $^ $(LDFLAGS)

$(HLIGHT_EXE): $(HLIGHTOBJECTS) $(COMMONOBJECTS)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
ifdef windir
	-$(CMD_RM) $(WIN32_HQBSP_EXE_BACKSLASH)
	-$(CMD_RM) $(WIN32_HVIS_EXE_BACKSLASH)
	-$(CMD_RM) $(WIN32_HLIGHT_EXE_BACKSLASH)
	-$(CMD_RM) common\*.o
	-$(CMD_RM) common\*.d
	-$(CMD_RM) hqbsp\*.o
	-$(CMD_RM) hqbsp\*.d
	-$(CMD_RM) hvis\*.o
	-$(CMD_RM) hvis\*.d
	-$(CMD_RM) hlight\*.o
	-$(CMD_RM) hlight\*.d
	-$(CMD_RM) *.o
	-$(CMD_RM) *.d
else
	-$(CMD_RM) $(WIN32_HQBSP_EXE) $(WIN32_HVIS_EXE) $(WIN32_HLIGHT_EXE) $(UNIX_HQBSP_EXE) $(UNIX_HVIS_EXE) $(UNIX_HLIGHT_EXE) *.[od] */*.[od]
endif

.PHONY: clean

-include *.d
