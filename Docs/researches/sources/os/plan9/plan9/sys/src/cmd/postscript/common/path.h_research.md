# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/path.h

Path constants for PostScript prologues, fonts, requests, and temporary files.

Key responsibilities:
- Defines absolute Plan 9 paths for translator prologues such as `dpost.ps`, `postbgi.ps`, `postprint.ps`, and related support files.
- Defines font, encoding, host font, PostScript library, request, and temp directories.

Notable behavior:
- Path values are compile-time defaults consumed by multiple tools and makefiles.
