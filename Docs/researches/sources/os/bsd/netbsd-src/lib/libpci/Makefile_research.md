# File Research: sources/os/bsd/netbsd-src/lib/libpci/Makefile

Read completely: 28 lines.

This builds `libpci` from local userland wrapper files plus `pci_subr.c` and `dev_verbose.c` from the kernel source tree. It installs `pci.h`, `pci.3`, and mlinks for config read/write and device information helpers.

It adds `${NETBSDSRCDIR}/sys` to include paths and source search paths.

Security/reliability notes: build-only file. The library is a userland bridge to kernel PCI ioctl interfaces.
