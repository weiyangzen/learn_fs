# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/wdir.c

This file wraps filesystem operations so all wiki data paths are relative to global `wikidir`.

Functions:
- `wname` builds `wikidir + "/" + relative`.
- `wopen`, `wcreate`, `wBopen`, `waccess`, and `wdirstat` call the corresponding Plan 9 filesystem operation on the expanded path and free it.

Role:
- Centralizes wiki directory prefixing for storage code in `io.c` and rendering/template reads.

Notable behavior:
- No path traversal checks are done here; callers are responsible for passing controlled relative paths.
