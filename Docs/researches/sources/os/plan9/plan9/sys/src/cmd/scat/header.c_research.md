# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/header.c

Reads DSS plate headers, the plate list, and mounts DSS jukebox disks.

Key functions:
- `getheader` locates a region `.hhh` header, parses 80-byte/FITS-like records, fills `Header.param`, detects AMD vs PPO coordinate modes, and computes RA/Dec parameter aggregates.
- `getplates` reads plate region records from local or jukebox paths into global `plate[]`.
- `dssmount` mounts the requested DSS disk via `JUKEFS` under `/n/juke` and caches the mounted disk number.

Behavior notes:
- Header parameter names map through `Hproto` into `Header.param` indexes shared with `sky.h`.
- Fallback paths check `/lib/sky/dssheaders`, then jukebox DSS 102 and DSS 061 locations.
- Missing header/plate data exits with file errors.
