# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k.c

Runtime dispatcher for m68k `libkvm` machine-dependent operations. Because one library build must support several m68k machines, it selects a `struct kvm_ops` table based on the machine name embedded in the kcore CPU header.

Key behavior:
- Matches `sun2`, `sun3`, `sun3x`, `gen68k`, or falls back to common m68k ops.
- Allocates `struct vmstate`, stores selected ops, computes page shift and page offset mask from kcore page size, then calls the selected init hook.
- Public MD hooks delegate `kvatop`, `pa2off`, and free operations to the selected ops.
- `_kvm_mdopen()` derives max user VA from `__ps_strings + 1`.

This file is the architecture-family multiplexer; actual translation lives in common/generic/sun modules.
