# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k_gen.c

Generic m68k translation implementation for newer generic kcore data. It exports `_kvm_ops_gen68k` and reconstructs MMU table indexing from the 68851-style TCR fields in the kcore header.

Key behavior:
- Allocates a private `kvm_gen68k_context` with page frame mask, significant VA mask, and up to four table-index descriptors.
- Validates page-shift, initial-shift, and table-index sizes from TCR.
- `mmu_tree_walk()` follows short descriptors from SRP through table levels, rejecting invalid/long descriptors.
- `_kvm_gen68k_kvatop()` handles relocation ranges, otherwise walks the MMU tree and adds page offset.
- `_kvm_gen68k_pa2off()` maps physical addresses through generic m68k RAM segment arrays.

This is the most data-driven m68k translator in the group.
