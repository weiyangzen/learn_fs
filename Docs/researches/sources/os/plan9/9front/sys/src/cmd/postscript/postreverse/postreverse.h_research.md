# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postreverse/postreverse.h

Small header for `postreverse.c`. It defines `Pages`, storing start/stop byte offsets and an `empty` flag for dummy forms-per-page pages, and declares `char *copystdin();`.

Integration points:
- Used by `postreverse.c` to type the global `pages[1000]` array.

Risks:
- Old-style function declaration only.
- `long` offsets mirror legacy `ftell` use and may be limiting on very large files.
