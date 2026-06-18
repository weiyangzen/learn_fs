# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiorom.c

Stub implementation of `%rom%`, intended as a compressed in-memory filesystem IODevice for embedded Ghostscript builds.

Structure:
- Defines `%rom%` as a filesystem IODevice with open-file support only.
- Allocates a small `romfs_state` during init, but does not attach it to `iodev->state`.
- `iodev_rom_open_file` ignores the requested filename and returns a stream over the fixed string `this came from the compressed romfs.`

Current state:
- The file documents intended ROM/static-data filesystem support but does not implement lookup, compression, file tables, status, or enumeration.
- It is best read as scaffold/prototype code rather than production ROM filesystem logic.
