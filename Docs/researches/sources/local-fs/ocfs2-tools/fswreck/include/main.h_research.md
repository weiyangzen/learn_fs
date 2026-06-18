# File Research: sources/local-fs/ocfs2-tools/fswreck/include/main.h

This is fswreck’s shared umbrella header.

Key content:
- Enables `_GNU_SOURCE`.
- Includes standard C/POSIX, GLib, Linux type, and libocfs2 headers.
- Defines fatal/warning macros:
  - `FSWRK_FATAL`
  - `FSWRK_COM_FATAL`
  - `FSWRK_FATAL_STR`
  - `FSWRK_WARN`
  - `FSWRK_WARN_STR`
- Defines local `max`, `min`, and `ARRAY_ELEMENTS`.
- Includes `fsck_type.h` and every fswreck module header.

Integration notes:
- All fswreck C files include this header, making it the central dependency surface.
- Fatal macros raise `SIGTERM` and exit, so most helper errors terminate the process rather than returning status.
