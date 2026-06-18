# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/scat.c

Main program and command interpreter for the `scat` sky catalog tool.

Key responsibilities:
- `main` initializes buffered stdin/stdout, optional catalog directory, initial `astro` data, then reads commands and dispatches `lookup`.
- Opens and caches catalog databases: SAO, NGC/IC, Abell, Messier index, names, Bayer names, constellation patches, and patch indexes.
- Loads records into the global dynamic `rec` array through `loadngc`, `loadsao`, `loadabell`, `loadplanet`, `loadpatch`, and `loadtype`.
- `flatten` recursively resolves symbolic records (`NGCN`, named records, constellation patches, patch lists) into concrete catalog records.
- `cull`, `sort`, `coords`, and `pplate` filter, de-duplicate, expand coordinate regions, and request DSS plate images.
- `lookup` parses user commands for object lookup, constellation lookup, `expand`, `plot`, `astro`, `plate`, `gamma`, `keep`, `drop`, named stars, and coordinate patches.
- `prrec`, `nameof`, `printnames`, and helper group functions format output.

Behavior notes:
- On-disk catalog integers are little-endian; `Long` and `Short` normalize them.
- `strings.c` is included directly for Greek, constellation, and object-name tables.
- Small result sets print full records; larger sets print a count.
- Name lookup supports quoted prose names and Bayer-style Greek/constellation names.

Risk/maintenance notes:
- Uses many fixed catalog-size constants and global file descriptors.
- `loadabell` contains a duplicated assignment to `cur->abell.ra`.
