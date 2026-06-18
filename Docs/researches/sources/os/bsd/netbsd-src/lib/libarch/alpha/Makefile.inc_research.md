# File Research: sources/os/bsd/netbsd-src/lib/libarch/alpha/Makefile.inc

Alpha `libarch` make include. When `MACHINE_ARCH` is `alpha`, it adds `alpha_bus_window.c`, `alpha_pci_conf.c`, `alpha_pci_io.c`, and `alpha_pci_mem.c` to `SRCS`.

This gates Alpha-specific userland hardware access helpers to Alpha builds only.
