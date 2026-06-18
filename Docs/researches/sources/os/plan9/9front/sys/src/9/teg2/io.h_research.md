# File Research: sources/os/plan9/9front/sys/src/9/teg2/io.h

Minimal Tegra I/O header. It defines `BUSUNKNOWN`, a zero `PCIWINDOW`, and `PCIWADDR(va)` as `PADDR(va)+PCIWINDOW`.

The RTL8169 driver uses `PCIWADDR` to convert CPU virtual packet/descriptor addresses into PCI-visible DMA addresses.
