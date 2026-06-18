# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/io.c

Low-level I/O, BIOS, vgactl, allocation, and dump formatting support for the VGA utility.

Core behavior:
- Provides `inportb/w/l()` and `outportb/w/l()` using Plan 9 `#P/iob`, `#P/iow`, and `#P/iol`.
- Reads and writes `#v/vgactl` attributes through cached parsing.
- Provides palette programming.
- Reads VGA BIOS from `#v/vgabios`, falling back to process memory.
- Caches BIOS reads in a static 64 KB buffer.
- Dumps BIOS as hex/ASCII if it finds a BIOS signature at `0xC0000` or `0xE0000`.
- Provides `alloc()`, `printitem()`, `printreg()`, and `printflag()` helpers.

Dependencies and integration:
- Used by almost every VGA controller backend.
- Depends on Plan 9 VGA and port-I/O devices.

Notable risks:
- `vgactlinit()` stores pointers into a mutable static buffer; cache invalidation is manual.
- BIOS fallback to `#p/<pid>/mem` is highly Plan 9 specific.
- `printflag()` has a fixed table for known flag bits and prints unknown bits numerically.
