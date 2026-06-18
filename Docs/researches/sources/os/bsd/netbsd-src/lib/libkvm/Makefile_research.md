# File Research: sources/os/bsd/netbsd-src/lib/libkvm/Makefile

Builds `libkvm`, the kernel virtual memory access library. Common sources are `kvm.c`, `kvm_file.c`, `kvm_getloadavg.c`, and `kvm_proc.c`; one machine-dependent `kvm_${arch}.c` source is selected by `KVM_MACHINE_ARCH`, `KVM_MACHINE_CPU`, `MACHINE_ARCH`, or `MACHINE_CPU`.

Special cases:
- i386 also builds `kvm_i386pae.c`.
- m68k also builds common/generic and sun-specific support files.
- sparc creates local `machine`/`sparc` symlinks for sparc64-with-sparc-arch header compatibility.
- The library uses shared-library directory support and `USE_FORT`.
