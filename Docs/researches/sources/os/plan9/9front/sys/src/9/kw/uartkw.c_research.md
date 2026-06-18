# File Research: sources/os/plan9/9front/sys/src/9/kw/uartkw.c

Kirkwood UART driver for the Marvell 16550-like console UART. It defines UART register layout and status/control bits, one controller, one console UART, interrupt-driven RX/TX, and polling getc/putc support.

`kw_enable` enables FIFO and RX/TX interrupts through the high interrupt bank. `kw_intr` services THR-empty and RX-data causes, dispatching to `uartkick` and `kw_read`. `kw_kick` pushes up to 16 bytes to the transmitter. Console setup binds `consuart` and applies `b115200 l8 pn s1 i1`.

Most line-control methods (`baud`, bits, stop, parity, modem, RTS/DTR/FIFO) are stubs returning success or doing nothing, so the port relies on existing firmware/default UART setup.

Notable risks: frequency is set to zero, baud programming is not implemented, and several paths lazily initialize `regs` because early print paths can run before normal PNP.
