# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/png_.h

Small include wrapper for libpng. It selects `<png.h>` when `SHARE_LIBPNG` is true and the local `"png.h"` otherwise.

The wrapper lets Ghostscript source depend on `png_.h` without knowing whether the build is linked to a shared system libpng or the bundled libpng source tree.

Filesystem relevance is none directly; this is image codec include plumbing.
