# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_powerpc64.c

PowerPC64 machine-dependent module with incomplete KVA translation. `_kvm_kvatop()` rejects live kernels and otherwise returns no translation. `_kvm_pa2off()` scans RAM segments in kcore CPU data and maps physical addresses to packed dump offsets.

`_kvm_mdopen()` uses the same `__ps_strings + 1` max-user-VA heuristic as 32-bit PowerPC.
