hmap utilities by Forest "LordHavoc" Hale ( havoc@telefragged.com )
Based on source code from id Software (Quake utilities) and Ritual Entertainment (Scourge of Armagon mission pack)
Website: http://icculus.org/twilight/darkplaces

Run the utilities with no parameters in a DOS prompt or Linux/UNIX terminal to get information about each.

Or read the source code (qbsp.c, vis.c, or light.c, respectively) to see the same usage information.

The sourcecode zip includes a Makefile for GNU make, a Makefile.mingw for mingw (make -f Makefile.mingw), and Microsoft Visual C++ 6.0 project files (open the hmap.dsw workspace).

How to use the new hlight light properties:
"wait" - affects size of light without affecting it's intensity - 1.0 default, 0.5 = bigger radius, 2 = smaller.
"_color" - 3 values (red green blue), specifies color of light, the scale of the numbers does not matter ("1 3 2.5" is identical to "1000 3000 2500").
"_lightradius" - limits light to this radius (and darkens light to make it blend well at the edges), only intended for switchable light styles so they don't cover whole rooms if you don't want them to.
"light" - can be one of four different formats:
quake: "light" "100" (intensity) white light but can be colored by "_color", this example is white light of intensity 100
hlight: "light" "100 50 30" (red green blue) this is the same as using "light" "100" "_color" "1 0.5 0.3", this example is orange light of intensity 100
halflife: "light" "100 255 255 200" (intensity red green blue) red/green/blue are 0-255 range, this example is yellowish-white light of intensity 100

hqbsp features:
Most errors report where the problem is (whether by line number in the .map file, or location in the map editor).
CheckFace: point off plane is now only a warning, and tries to self-correct.
Rewritten wad loader which should be far less finicky than the original, and allows multiple wads.
Water/slime/lava is transparent by default (hqbsp -nowater to disable this).
-darkplaces option to increase subdivide size to 4080 (really huge polygons), can make a map much faster but requires darkplaces engine to be used, or any other engine implementing 256x256 texel lightmaps.
Support for very large maps (up to +-32767 units, the very limits of the .bsp file format).
Hipnotic rotation support.
Greatly increased limits for everything.
Can vis a leaky map (use hqbsp -noforcevis if you want vis to fail on a leaky map).
Shows useful information if run with no parameters.
Can compile .map files using HalfLife WorldCraft texture alignment

hvis features:
Can disable liquid sounds (-noambient, -noambientwater, -noambientsky, -noambientlava (quake never used ambient lava sounds though)).
RVis optimization for faster vising (this does cause a 0.001% degradation in vis quality, too small to care about, -norvis to disable).
Defaults to -level 4 vis quality (which is often faster than vis's default of level 2).
Shows useful information if run with no parameters.

hlight features:
More realistic attenuation.  (original light.exe method is not supported in any way, nor are tyrlite modes, this is intentional; only realistic is supported)
Falloff scaling from arghlite.  (but remember the attenuation is quite different already)
Colored lighting (.lit file) for enhanced engines while not breaking classic quake.
16 sample lightmap antialiasing (hlight -extra4x4).
Better handling of floor-meets-wall seams in lighting, none of those messy problem cases seen in the original light.exe.
-relight option to make a .lit file for an existing .bsp without modifying the .bsp in any way (this will not add color, unless the lights contain color info already).
Support for extremely large polygons as produced by hqbsp -darkplaces.
Hipnotic rotation support.
Uses vis data to light map faster (-nolightvis to ignore the vis data).
Shows useful information if run with no parameters.

Probably other features I forgot to mention...
