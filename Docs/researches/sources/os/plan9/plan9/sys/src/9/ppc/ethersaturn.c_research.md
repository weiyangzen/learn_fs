# File Research: sources/os/plan9/plan9/sys/src/9/ppc/ethersaturn.c

## Role

Ethernet hardware driver for the Saturn board Ethernet block, registered as card type `"saturn"`.

## Main Data

Maps Saturn Ethernet control/status, interrupt, MAC, and MII registers. Uses a fixed packet memory window at `Ethermem`, with 14 RX slots and 2 TX slots. `Ctlr` tracks TX ring state, RX last index, active flag, interrupt count, and overflow stats. A default global `etheraddr` is provided.

## Control Flow

`reset` disables RX, allocates controller state, installs callbacks, reads MAC address from hardware, enables RX and interrupts, and marks active. `transmit` locks the controller, fills TX packet memory from the output queue, and starts transmission if idle. `interrupt` acknowledges events, handles TX done/retry state, loops over RX slots until hardware index catches up, allocates blocks for received frames, sends them to `etheriq`, and logs unhandled interrupts.

## Dependencies

Depends on `msaturn.h`, `etherif.h`, Plan 9 queues/blocks, and board interrupt `Vecether`.

## Risks

Uses fixed shared packet memory and small TX ring. Some interrupt conditions only log. MII registers are defined but not used in this file. `reset` prints register state during initialization.
