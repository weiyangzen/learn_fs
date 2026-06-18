# File Research: sources/os/plan9/9front/sys/src/9/bcm/fns.h

BCM architecture function declaration header.

Key declarations:
- Architecture device registration, reset/reboot/watchdog, boot args, cache operations, MMU operations, clock, coprocessor, DMA, GPIO, firmware, framebuffer, interrupt, UART, and process/trap helpers.
- Floating-point hardware/emulation entry points.
- Port-called helpers for delay, interrupt level, alignment checks, idle, and kernel register setup.
- Address conversion macros `KADDR` and `PADDR`.

Dependencies:
- Extends `../port/portfns.h`.

Research notes:
- This is the principal cross-file API surface for the BCM port.
