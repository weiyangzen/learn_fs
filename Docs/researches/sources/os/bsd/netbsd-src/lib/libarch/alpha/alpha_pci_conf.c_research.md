# File Research: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_conf.c

Alpha PCI configuration-space helper code. `alpha_pci_conf_read()` fills a `alpha_pci_conf_readwrite_args` structure and invokes `sysarch(ALPHA_PCI_CONF_READWRITE)`, returning `0xffffffffU` on failure.

`alpha_pci_conf_write()` uses the same sysarch operation with `write=1` and ignores the syscall result. These routines expose simple userland PCI config read/write helpers.
