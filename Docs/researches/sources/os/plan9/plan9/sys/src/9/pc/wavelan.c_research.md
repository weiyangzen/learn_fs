# File Research: sources/os/plan9/plan9/sys/src/9/pc/wavelan.c

## Purpose
Lucent/Orinoco WaveLAN IEEE 802.11 Hermes driver core for Plan 9 Ethernet devices, covering command/LTV access, attach/reset, TX/RX, WEP settings, scanning, stats, interrupts, timer recovery, power hooks, and control commands.

## Main Interfaces
- Exports CSR helpers `csr_outs`, `csr_ins`, `w_intdis`, `w_cmd`, `ltv_outs`, `ltv_ins`, `w_inltv`.
- Exports Ethernet callbacks: `w_attach`, `w_detach`, `w_interrupt`, `w_transmit`, `w_ifstat`, `w_ctl`, `w_promiscuous`, `w_multicast`, `w_power`.
- Exports `wavelanreset(Ether*, Ctlr*)`.
- Exports `wavenames[]` with recognized PCMCIA/card names.

## Implementation Notes
- CSR access supports either port I/O or PCI memory-mapped I/O; MMIO registers are indexed as 16-bit registers spaced like 32-bit slots.
- Hermes commands are synchronous: wait for `WCmdBusy` clear, issue command/parameter, wait for `WCmdEv`, validate status, and acknowledge.
- LTV helpers implement card configuration reads/writes for ESSID, channel, port type, MAC, power management, WEP keys, stats, and scan results.
- `w_enable` resets/initializes card operation, programs all controller settings, allocates transmit buffers, and enables interrupts.
- RX path reads `WFrame`, distinguishes RFC1042/tunnel/WMP from native 802.3, builds an Ethernet packet, queues it via `etheriq`, and smooths signal/noise.
- TX path dequeues `ether->oq`, constructs 802.11/SNAP framing when needed, writes frame and payload to allocated card memory, and starts reclaiming transmit.
- Interrupt handling processes RX, TX, allocation, info, TX error, and info-drop events, then tries to start another transmit.
- `w_timer` polls missed events, handles transmit watchdog timeouts by re-enabling the card, and periodically requests stats/scan info.
- `w_option` parses control commands for ESSID/station/channel/mode/IBSS/WEP keys/txkey/power management and `w_ctl` applies them by re-enabling the card.

## Dependencies And Risks
- File comments explicitly flag weak documentation, endian/alignment concerns, long interrupt-disabled sections, receive-watchdog concerns, and locking TODOs.
- WEP key parsing supports ASCII 5/13-byte and hex 10/26-digit forms; stat output hides key contents unless `SEEKEYS` is enabled.
- `w_detach` posts a note to kill the timer process and clears `ether->ctlr`; timer shutdown depends on observing that change.
- Multicast filtering is not implemented; enabling multicast falls back to promiscuous mode.
