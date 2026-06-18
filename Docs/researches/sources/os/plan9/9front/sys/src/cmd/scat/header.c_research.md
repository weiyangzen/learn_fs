# File Research: sources/os/plan9/9front/sys/src/cmd/scat/header.c

Purpose: Reads DSS plate headers and plate inventory, and mounts jukebox-backed DSS media when local files are unavailable.

Key routines:
- `getheader`: finds `<region>.hhh` locally or through DSS jukebox paths, parses FITS-like header fields into `Header.param`, computes plate RA/Dec in radians, and detects AMD coefficient availability.
- `getplates`: reads `lo_comp.lis`, fills global `plate[]` with region, center coordinates, and disk number.
- `dssmount`: mounts the jukebox service and 9660 filesystem for a requested DSS disk, caching the currently mounted disk number.

Integration: Used by `image.c` to choose and read the best DSS plate for a requested sky coordinate. Depends on `Hproto` mapping from header keyword to `Header.param` index.

Risks:
- Hard-coded paths `/lib/sky/dssheaders`, `/n/juke`, `/n/dss`, `/srv/tcp!jukefs`, and `/srv/9660`.
- Header parsing lowercases token names through `getword`.
- `getplates` caps global storage at `plate[2000]` and warns if too small.
