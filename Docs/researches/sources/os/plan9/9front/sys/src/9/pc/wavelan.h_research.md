# File Research: sources/os/plan9/9front/sys/src/9/pc/wavelan.h

Shared definitions for the Lucent WaveLAN/Hermes wireless driver.

Key contents:
- LTV type codes for stats, scan, link, port type, MAC, ESSID, channel, AP density, max length, power management, WEP, keys, transmit key, station ID, current network, base station, and tick settings.
- Controller constants for default IRQ/I/O base, I/O window length, command timeout, port modes, transmit rates, key sizes, frame offsets, and Hermes registers/events.
- Hermes command and event bits, frame status values, SNAP header constants, and 802.11/802.3 data offsets.
- Structs:
  - `WStats`: hardware transmit/receive counters.
  - `WScan`: scan result sample with channel, signal/noise, BSSID, beacon interval, capabilities, and SSID.
  - `WFrame`: Hermes frame descriptor and embedded Ethernet/SNAP fields.
  - `WKey`: WEP key length and data.
  - `Wltv`: union-backed Lucent LTV record.
  - `Stats`: driver-side counters and signal/noise state.
  - `Ctlr`: full driver controller state, configuration, TX buffers, WEP state, PCI/MMIO state, and embedded stats.
- Prototypes for WaveLAN CSR access, LTV access, options, attach, interrupt, transmit, status, control, promiscuous/multicast hooks, and reset.

Notable dependencies:
- Plan 9 network constants such as `Eaddrlen`, `Ether`, and `Ureg` are expected from including translation units.
- PCI fields are present but abstracted through `Ctlr`.

Research notes:
- The header mixes hardware protocol, driver state, and exported driver API in one file.
- The `DEBUG` macro is compiled out by default.
- `Ctlr` embeds both `Stats` and `WStats`, making driver and hardware counters directly accessible through a single controller pointer.
