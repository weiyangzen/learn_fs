# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gconf.h

Wrapper for the generated Ghostscript configuration header.

Key points:
- Intentionally has no double-inclusion guard because it is included repeatedly with different macro definitions.
- Includes `gconfig.h` by default.
- If `GCONFIG_H` is defined, includes that macro-specified header instead.

Dependencies and interactions:
- Used by `gconf.c`/`gconfig.c` to generate tables from macro entries.

OS/filesystem relevance:
- Indirect; configuration entries include IODevices and initialization files.
