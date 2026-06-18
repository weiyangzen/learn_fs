# File Research: sources/os/plan9/9front/sys/src/9/bcm64/rebootcode.s

ARM64 reboot trampoline copied to low physical memory.

Key responsibilities:
- Copies replacement code/image to destination.
- Disables MMU and caches through system-register updates.
- Invalidates local TLB state.
- Branches to new entry or waits when no entry is provided.

Important behavior:
- Runs from physical low memory after `rebootjump()` copies it to `REBOOTADDR`.
- Uses raw system-register encodings for reboot-safe operation independent of normal kernel mappings.

Dependencies:
- ARM64 system register definitions and `main.c` reboot path.
