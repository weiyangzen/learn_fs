# File Research: sources/os/plan9/9front/sys/src/9/pc/uartaxp.c

## Role

`PhysUart` driver for AvanstarXp PCI multiport UART cards using an on-board control program and shared control blocks.

## Main Interfaces

- Exports `PhysUart axpphysuart` named `AvanstarXp`.
- PnP path `axppnp()` scans PCI communication devices and matches vendor/device `0x114f/0x6001`.
- Provides standard UART operations: enable, disable, kick, break, baud, bits, stop, parity, modem control, RTS/DTR, status, and FIFO stub.

## Key Behavior

- Defines global control block (`Gcb`) and per-channel control block (`Ccb`) layouts shared with the adapter firmware.
- `axpalloc()` maps PCI runtime registers and local memory, resets the adapter, downloads `uartaxpcp` from `uartaxp.i`, starts it, verifies board type, and creates up to 16 `Uart` channels.
- Channel commands are issued by writing `Ccb.cc` and waiting for firmware to clear it, either by polling or sleeping on command-service interrupts.
- Transmit path writes bytes into the adapter output circular buffer and updates `obwp`.
- Receive interrupt path drains adapter input circular buffers and calls `uartrecv()`.
- Interrupt handler uses doorbell status and xchg-cleared service request registers for input, output, command, modem, and error events.
- Modem-control code tracks CTS/DSR/DCD and hangup conditions.

## Dependencies And Assumptions

- Depends on the generated/included firmware image `uartaxp.i`.
- Requires PCI memory BAR0 and BAR2 mappings.
- Shared service request fields must be accessed using `xchgw()`, as noted by the file.
- FIFO control is a no-op because buffering is handled by adapter firmware/shared memory.

## Research Notes

- Unlike the simple 8250 driver, this is a firmware-mediated multiport serial driver.
- Initialization has several board-seating/distribution-panel failure messages, indicating hardware deployment experience shaped the driver.
