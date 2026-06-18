# File Research: sources/os/plan9/plan9/sys/src/9/port/rebootcmd.c

Loads a new kernel/program image and invokes the platform reboot hook.

Key functions:
- `readn` repeatedly reads exact byte counts from a channel, advancing `c->offset`.
- `readelfhdr` parses 32-bit ELF headers and extracts entry/text/data sizes.
- `readelf64hdr` does the same for 64-bit ELF headers.
- `setbootcmd` quotes remaining argv into the `bootcmd` kernel environment variable.
- `rebootcmd` opens the requested executable, recognizes a.out or ELF, reads text/data into a contiguous buffer, sets `bootfile` and `bootcmd`, and calls `reboot(entry, image, size)`.

Important behavior:
- Supports optional architecture-specific `parseboothdr`.
- Rounds text placement to page boundary before appending data.
- `argc == 0` exits immediately.
- Panics if `reboot` returns.

Role:
- Portable part of kernel reboot-from-file command handling.
