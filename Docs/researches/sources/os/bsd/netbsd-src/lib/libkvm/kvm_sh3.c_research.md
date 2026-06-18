# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sh3.c

SH3 machine-dependent `libkvm` stub. `_kvm_kvatop()` and `_kvm_pa2off()` both report not implemented. Initialization succeeds and `_kvm_mdopen()` sets user VA bounds from SH3 VM constants.

Crash dump address translation is not usable in this module as written.
