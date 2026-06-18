# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/png_.h

Minimal wrapper for including libpng headers.

If `SHARE_LIBPNG` is true, it includes system `<png.h>`; otherwise it includes the bundled `"png.h"`. This lets the Ghostscript build switch between external and bundled libpng.

No filesystem logic is present.
