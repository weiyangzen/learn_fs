# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_alpha.c

Implements Alpha dead-kernel KVA translation. It handles direct-mapped `K0SEG` addresses and page-table translated `K1SEG` addresses.

Key behavior:
- Reads L1, L2, and L3 Alpha PTEs using the level indexes and `lev1map_pa` from the kcore CPU header.
- Validates `ALPHA_PTE_VALID` at each level.
- Computes physical address from PFN and page offset.
- `_kvm_pa2off()` walks physical RAM segments stored after the CPU kcore header.

User VA bounds are set from Alpha VM constants in `_kvm_mdopen()`.
