# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_i386.c

Implements i386 machine-dependent crash dump KVA translation and dispatches between non-PAE and PAE walkers.

Key behavior:
- `_kvm_initvtop()` checks `cpu_kcore_hdr_t.pdppaddr` for `I386_KCORE_PAE`.
- `_kvm_kvatop()` delegates to `_kvm_kvatop_i386()` or `_kvm_kvatop_i386pae()`.
- Non-PAE walker reads PDE and PTE entries, supports 4MB large pages, validates `PTE_P`, and computes physical address plus contiguous byte count.
- `_kvm_pa2off()` maps physical addresses through packed RAM segments.

User VA bounds use i386 VM constants.
