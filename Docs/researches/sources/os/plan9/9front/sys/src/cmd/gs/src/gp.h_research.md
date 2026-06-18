# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp.h

Ghostscript platform-abstraction interface header. It declares the cross-platform API implemented by the many `gp_*.c` files.

Key contents:
- Initialization and exit hooks: `gp_init`, `gp_exit`, `gp_do_exit`.
- Error string, realtime/usertime, readline, and stdin-read interfaces.
- Display environment lookup for X-like display devices.
- File naming constants and platform-specific file mode strings.
- Scratch-file creation, byte-oriented `gp_fopen`, binary/text mode switching, and path-combination helpers.
- Mac resource-fork access through `gp_read_macresource`.
- Persistent cache API for typed key/value buffers.
- Printer open/close abstraction.
- File enumeration API for wildcard expansion.
- Native font enumeration API.

Research notes:
- `gp_getenv` lives in `gpgetenv.h` and synchronization lives in `gpsync.h`; this header deliberately excludes those.
- Path helper comments document Unix, Windows, Mac, and VMS semantics.
- Several comments contain historical misspellings such as “partent” and “meanful”; corresponding API names preserve them.
