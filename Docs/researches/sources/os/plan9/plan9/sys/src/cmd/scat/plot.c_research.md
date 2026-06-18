# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/plot.c

Plots selected sky catalog records into a Plan 9 image and invokes `astro` for planet/observer data.

Key responsibilities:
- `plotopen` initializes draw display, colors, stipple images, and font.
- Map helpers convert RA/Dec into a stereographic projection, with optional zenith-up observer orientation.
- `bbox`, `inbbox`, and `gridra` compute plot extents and grid spacing.
- `plot` parses flags (`nogrid`, `zenithup`, `notext`, `alltext`, `dx`, `dy`, `nogrey`), flattens records, draws grid/labels, then draws planets, stars, Abell clusters, and NGC object symbols.
- `astro` runs `/bin/astro -p`, records site/sidereal data, prints output, and rebuilds the global `planet` list.
- `parseplanet` parses one astro planet output line.

Behavior notes:
- RA ranges wider than 270 degrees trigger folded plotting around 180 degrees.
- Planets are moved to the end of the record list so they render in front, with moon and shadow ordering handled specially.
- Different NGC object types use distinct symbols: galaxy ellipses, planetary nebula rings/crosses, nebula boxes, open cluster stipple, and globular cluster crosshairs.

Risk/maintenance notes:
- The file relies on map library globals/functions (`orient`, `stereographic`, `normalize`) and Plan 9 draw globals.
- `plot` contains dense rendering logic and global mutable projection state.
