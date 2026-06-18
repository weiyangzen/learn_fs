# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_hppa.c

Stub/partial HPPA machine-dependent `libkvm` implementation. The intended page-directory/page-table walk is present under `#if 0`, but active code reports failure for `_kvm_kvatop()` and returns zero for `_kvm_pa2off()`.

`_kvm_mdopen()` still sets normal user VA bounds from HPPA VM constants. Crash dump virtual address translation is effectively unimplemented.
