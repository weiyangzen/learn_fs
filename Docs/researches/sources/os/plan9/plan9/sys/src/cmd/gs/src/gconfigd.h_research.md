# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconfigd.h

Generated Ghostscript default path/version header for Plan 9.

Key points:
- Defines `GS_LIB_DEFAULT` as `/sys/lib/ghostscript:/sys/lib/ghostscript/font:/sys/lib/postscript/font`.
- Defines empty `GS_CACHE_DIR`.
- Enables `SEARCH_HERE_FIRST`.
- Defines documentation directory `/sys/src/cmd/gs/doc`.
- Defines init file `gs_init.ps`.
- Defines revision `853` and revision date `20051020`.

Dependencies and interactions:
- Used by Ghostscript startup path and version logic.

OS/filesystem relevance:
- Directly defines default filesystem search paths for Ghostscript libraries and fonts on Plan 9.
