# File Research: sources/os/plan9/9front/sys/src/9/lx2k/io.h

LX2K I/O constants. It defines interrupt numbering for GIC PPIs/SPIs used by timer, UART, USB, and PCIe, along with `BUSUNKNOWN`, `PCIWINDOW`, and `PCIWADDR`.

The values feed clock setup, PL011 UART, xHCI, PCIe root complex setup, and generic interrupt registration.

Notable risks: all device IRQs are hard-coded to LX2K wiring.
