# File Research: sources/os/plan9/9front/sys/src/9/imx8/io.h

Role: i.MX8 interrupt-number and PCI bus helper definitions.

Key contents:
- Defines `IRQfiq`, PPI/SPI bases, generic timer IRQs, LCD/VPU/uSDHC/UART/I2C/RDC/USB/SCTR/GPIO/PCI/SAI/ENET interrupt numbers.
- Defines `BUSUNKNOWN` as `-1`.
- Defines `PCIWADDR(x)` as physical address plus `PCIWINDOW`, with `PCIWINDOW` currently zero.

Dependencies:
- Included broadly by i.MX8 C files for IRQ constants and bus sentinel values.

Notes:
- IRQ numbering matches GIC SPI/PPI scheme with `SPI` offset 32.
