# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_riscv.c

RISC-V machine-dependent `libkvm` module. KVA-to-PA translation is not implemented; `_kvm_kvatop()` returns no translation for dead kernels. `_kvm_pa2off()` scans physical RAM segments in the kcore CPU data and returns packed dump offsets.

`_kvm_mdopen()` sets user VA bounds from RISC-V VM constants. The file header comment still says OR1K, indicating likely copy-forward scaffolding.
