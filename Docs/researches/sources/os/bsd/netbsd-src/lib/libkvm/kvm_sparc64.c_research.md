# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sparc64.c

SPARC64 machine-dependent libkvm crash-dump address translation. `_kvm_kvatop()` handles new-format wired 4MB mappings, per-CPU mappings, old text/data mappings, then walks the kernel segment/directory/table TTEs to derive a physical address.

`_kvm_pa2off()` maps sparse physical RAM segments to packed dump offsets. `_kvm_mdopen()` derives user VA bounds from `__ps_strings`.
