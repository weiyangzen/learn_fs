# File Research: sources/os/plan9/9front/sys/src/9/ppc/ethersaturn.c

Ethernet driver for the Saturn/UCU board Ethernet block.

Key responsibilities:
- Defines Saturn Ethernet control/status/MII/MAC registers, frame memory layout, and ring sizes.
- Copies queued transmit packets into hardware frame slots and starts transmission when idle.
- Handles TX done, RX done, TX retry, and unhandled interrupt bits.
- Receives frames from Ethernet frame memory into Plan 9 blocks and passes them to `etheriq()`.
- Reads the MAC address from hardware registers, enables RX, enables selected interrupts, and registers the interrupt handler.
- Registers as `addethercard("saturn", reset)`.

Dependencies:
- Uses Saturn vector constants from `msaturn.h`, Plan 9 Ethernet queues, and board interrupt acknowledgement.

Notable behavior:
- Uses 14 RX frame slots and 2 TX slots, with `Nrx + Ntx` constrained to 16.
