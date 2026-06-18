# File Research: sources/os/plan9/9front/sys/src/cmd/scat/scat.c

Purpose: Main interactive astronomy catalog command. It loads binary sky catalogs, parses user commands, prints records, filters record sets, expands sky regions, plots charts, and displays DSS plates.

Major components:
- Catalog globals: SAO, NGC/IC, Messier index, names, Bayer entries, constellations, patch indexes.
- Startup: initializes `bin`/`bout`, optionally changes catalog directory, runs initial `astro`, then reads commands from stdin.
- Loaders: `loadsao`, `loadngc`, `loadabell`, `loadpatch`, `loadtype`, plus `nameopen`, `patchopen`, `mopen`, `constelopen`.
- Endian helpers: `Long` and `Short` convert little-endian on-disk fields.
- Record processing: `flatten` expands patch, named, and type records into concrete records; `sort` deduplicates non-planet records.
- Filtering: `cull` keeps or drops by magnitude, catalog, and object type.
- Lookup command parser: supports `sao`, `ngc`, `ic`, `abell`, `m`, constellations, coordinates, named stars, `expand`, `plot`, `astro`, `plate`, `gamma`, `keep`, `drop`, `flat`, and `print`.
- Printing: `prrec`, `nameof`, `printnames`, `ngcstring`, `dist_grp`, `rich_grp`.
- Star-name handling: `togreek`, `fromgreek`, `parsename`.

Integration: Central module for `scat`; calls support code in every other scat file.

Risks:
- Many fixed-size catalog constants and arrays are baked in.
- Binary catalog layout and little-endian fields must match `sky.h` packed structures.
- Some checks have old C idioms and subtle bugs, for example `if(j == 0)` in name lookup compares against absolute count after `j = nrec`.
- `#include "strings.c"` embeds data definitions directly into this translation unit.
