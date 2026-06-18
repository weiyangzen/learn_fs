# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jerror_.h

Small Ghostscript wrapper for IJG `jerror.h`. It exists to make the include target depend on the build choice represented by `SHARE_JPEG`.

Behavior:
- If `SHARE_JPEG` is true, it includes the system/shared JPEG header with `<jerror.h>`.
- Otherwise, it includes the local vendored header with `"jerror.h"`.
- The include guard is `jerror__INCLUDED`.

The wrapper lets other Ghostscript makefile/header rules depend on `jerror_.h` without hardcoding whether JPEG is built locally or supplied externally.

Filesystem relevance: none directly. It is build-time codec plumbing in the 9front Ghostscript source tree.
