Quake1 portal gun
=================

A portal inspired game using Quake1 engine based on:
http://www.moddb.com/mods/quake-portal-gun

Video of the gameplay:  
https://www.youtube.com/watch?v=KcJn5ba0928

How to play
===========

Controls are defined in autoexec.cfg. It's inspired by wecreatestuff's version of the game:

[p] - portal gun.

[q] - fire blue portal.

[e] - fire yellow portal.

[f] - grab item.

[w][s][a][d] - movement.

How to build the game data
==========================

You don't need to have original proprietary Quake 1 game data to play.

**Using GNU/Linux:**
```
$ cd openquartz/pak0/
$ make && make install
```

and it will copy all *.pak files into portal/id1 folder.just switch to that folder and run from command line your favourite quake engine (darkplace or ezQuake...)

Hope you enjoy it!
