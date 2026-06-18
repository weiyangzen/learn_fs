# File Research: sources/os/plan9/9front/sys/src/cmd/scat/plot.c

Purpose: Generates graphical sky charts from the current `scat` record set and obtains planet positions from `/bin/astro`.

Major areas:
- Display setup: `plotopen` initializes draw display, colors, stipples, and font.
- Projection math: vector helpers and `heavens` implement Doug McIlroy's observer-upright stereographic sky projection.
- Mapping: `setmap`, `maptoxy`, and `map` convert milliarcsecond RA/Dec to screen points.
- Bounds: `bbox`, `inbbox`, and `gridra` compute chart bounds and grid spacing.
- Rendering: `plot` draws coordinate grid, labels, stars, Abell clusters, galaxies, nebulae, clusters, and planets.
- Planet support: `runcommand`, `parseplanet`, and `astro` invoke `/bin/astro -p`, parse output, and store `Planetrec` values.

Integration: Depends on `map.h`, `draw`, global `rec/nrec`, `flatten`, `nameof`, and coordinate helpers from `scat.c`/`util.c`.

Risks:
- Uses global projection and map state.
- `parseplanet` assumes fixed-width astro output and mutates the input line at byte 10.
- Some drawing paths assume `font` is available; `plotopen` only warns if it cannot open the font.
- Planet sorting mutates the record array to render planets and shadow in front.
