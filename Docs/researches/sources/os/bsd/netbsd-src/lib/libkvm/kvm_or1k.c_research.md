# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_or1k.c

OR1K machine-dependent `libkvm` module. KVA-to-PA translation is not implemented; `_kvm_kvatop()` returns no translation for dead kernels. `_kvm_pa2off()` does work: it scans physical RAM segments in the CPU kcore data and returns the packed dump offset for a matching physical address.

`_kvm_mdopen()` sets user VA bounds from OR1K VM constants.
