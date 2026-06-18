# File Research: sources/os/plan9/9front/sys/src/9/arm64/rebootcode.s

ARM64 reboot trampoline copied to a physical/identity-mapped address.

Key behavior:
- Copies replacement kernel code to the requested entry address.
- Cleans and invalidates caches.
- Disables MMU, data cache, and instruction cache in `SCTLR_EL1`.
- Invalidates local TLB and caches again.
- Clears argument registers and returns to the copied entry address through `LR`.

Dependencies:
- Included into `main.c` as `rebootcode.i` and copied to `REBOOTADDR`.

Research notes:
- Designed to execute outside normal high-half kernel mappings during reboot.
