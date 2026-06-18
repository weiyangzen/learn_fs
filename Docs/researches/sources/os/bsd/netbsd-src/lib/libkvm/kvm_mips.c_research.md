# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_mips.c

Implements MIPS machine-dependent crash dump KVA translation.

Key behavior:
- Rejects user-space virtual addresses.
- Handles direct-mapped cached/uncached segments (`KSEG0`, `KSEG1`, and 64-bit `XKPHYS` where applicable).
- For mapped kernel space, validates the address against `sysmapsize`, reads a PTE from `sysmappa`, validates `pg_v`, and computes the physical address using kcore frame/shift fields.
- `_kvm_pa2off()` maps physical addresses through RAM segments after the CPU kcore header.

User VA bounds use MIPS VM constants.
