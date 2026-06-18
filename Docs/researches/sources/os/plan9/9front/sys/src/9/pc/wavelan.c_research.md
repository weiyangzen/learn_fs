# File Research: sources/os/plan9/9front/sys/src/9/pc/wavelan.c

Lucent WaveLAN IEEE 802.11 / Hermes controller driver core for Plan 9 Ethernet integration. It handles register I/O, Hermes command execution, LTV configuration records, transmit/receive framing, stats and scan reports, timer watchdogs, power, attach/detach, control commands, and Ethernet callbacks.

Key behavior:
- CSR helpers support both port-mapped and PCI memory-mapped devices. Memory-mapped Hermes registers are indexed as 16-bit values spaced like 32-bit registers.
- `w_cmd` waits for command readiness, issues Hermes commands, waits for command-complete events, acknowledges them, and validates status.
- `w_seek`, `w_read`, and `w_write` select card buffer IDs and offsets through access channels, then stream words through `WR_Data0` / `WR_Data1`.
- LTV helpers read and write Lucent Length-Type-Value records for MAC address, ESSID, port type, WEP keys, channel, power management, transmit rate, stats, and scan results.
- `w_enable` initializes the card, applies controller options, programs MAC address and WEP state, enables the controller, allocates transmit frame buffers, and enables interrupts.
- `w_rxdone` reads a received Hermes frame, translates 802.11/RFC1042/SNAP or 802.3 payloads into Ethernet blocks, queues them with `etheriq`, and updates signal/noise smoothing.
- `w_txstart` pulls from the Ethernet output queue, constructs either RFC1042/SNAP or 802.3 transmit headers, writes frame data into the card, and starts transmit/reclaim.
- `w_intr` handles RX, TX, allocation, info, TX error, and info-drop events under the controller lock, then tries to continue queued transmit.
- `w_timer` periodically polls missed events, handles transmit watchdog recovery, requests card stats, and triggers base-station scans.
- `w_ifstat` reports driver counters, card status, association info, WEP state, and accumulated hardware stats.
- `w_option` parses control commands for ESSID, station name, channel, mode, IBSS, WEP encryption, clear-packet exclusion, keys, transmit key, and power management.
- `wavelanreset` initializes default controller state, reads the station MAC, wires Ethernet callbacks, and registers the interrupt handler.

Notable dependencies:
- `wavelan.h` for Hermes register constants, LTV types, frame layout, and `Ctlr`.
- Plan 9 Ethernet interfaces: `netif.h`, `etherif.h`, `Ether`, `Etherpkt`, queues, scan readers.
- Kernel block allocation and interrupt primitives.

Research notes:
- The file documents known bugs: endian/alignment/mem-IO concerns, receive watchdog interrupts, power management, multicast filtering, and locking.
- Many low-level routines assume the caller already holds the controller interrupt lock.
- The timer intentionally polls event status because the hardware/driver can miss receive interrupts.
- WEP key support is legacy and hidden in stats output unless `SEEKEYS` is enabled.
- `w_detach` posts a kill note to the timer process and clears `ether->ctlr`, but the timer loop observes that asynchronously.
