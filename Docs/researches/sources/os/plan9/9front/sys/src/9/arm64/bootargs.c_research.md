# File Research: sources/os/plan9/9front/sys/src/9/arm64/bootargs.c

Implements ARM64 boot configuration parsing for 9front’s QEMU-style ARM64 kernel.

Key behavior:
- Maintains a small case-insensitive `name=value` configuration table with override semantics.
- Parses existing `BOOTARGS` as newline-separated `plan9.ini` content.
- Parses flattened device tree data at `DTBADDR`, including `/memory` `reg`, `/cpus/cpu*` `reg`, and `/chosen` `bootargs`.
- Derives `*maxmem` from the memory node when absent.
- Counts CPU nodes and installs `*ncpu` unless the user provided one.
- Exposes `getconf`, `setconfenv`, and `writeconf` for kernel configuration and reboot persistence.

Dependencies:
- Uses Plan 9 string/token helpers, `KADDR`, `cankaddr`, `BOOTARGS`, and kernel environment helpers.

Research notes:
- Device-tree parsing is intentionally narrow and only extracts early boot configuration needed by the port.
- `writeconf` serializes the live kernel environment back into `BOOTARGS` for reboot.
