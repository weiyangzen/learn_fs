# File Research: sources/os/bsd/netbsd-src/lib/libarch/arm/arm_sync_icache.c

Tiny public wrapper for synchronizing an ARM instruction-cache range.

Key behavior:
- Exports `int arm_sync_icache(uintptr_t addr, size_t len)`.
- Fills `struct arm_sync_icache_args` with `addr` and `len`.
- Calls `sysarch(ARM_SYNC_ICACHE, &p)`.

Dependencies:
- `machine/sysarch.h` for `ARM_SYNC_ICACHE` and argument layout.

Notes:
- Intended for generated/self-modifying code or code loaders that need I-cache coherency.
