# File Research: sources/os/plan9/9front/sys/src/9/port/etheriwl.c

Implements the Intel Wi-Fi Link driver for many Intel PCI wireless chip families, from 4965/5000/6000-era devices through 7000/8000/9000 family devices. It relies on firmware from `/boot` or `/lib/firmware`.

The file defines large hardware register maps, flow-handler registers, scheduler registers, firmware TLV parsing, EEPROM/NVM access, DMA ring setup, RX/TX queues, firmware paging memory, calibration state, station/context state, and controller state. `iwlpci` discovers supported Intel PCI IDs and maps BAR0; `iwlpnp` binds a controller to an `Ether` device and installs hooks.

Firmware handling includes `readfirmware`, `crackfw`, `loadsections`, `loadfirmware1`, `ucodestart`, and `boot`. It supports both older boot-code paths and newer section-loading paths, including init firmware calibration followed by main firmware runtime.

Runtime configuration sends firmware commands for PHY, MAC, binding contexts, stations, multicast filter, power mode, MCC/LAR, Bluetooth coexistence, calibration, paging, and TX antenna setup. `rxon` reconciles current channel/BSSID/AID/promiscuous settings and programs older or newer firmware families through `rxon6000` or 7000+ context commands.

Transmit builds firmware TX commands from Wi-Fi nodes, rates, antenna masks, ACK/RTS/protection requirements, station ids, and packet blocks, then queues them through `qcmd`. Receive drains the RX ring, handles command completions, firmware alive/errors, calibration records, NVM responses, time events, TX status, RX PHY timestamps, and received frames forwarded to `wifiiq`.

Interrupt handling disables/re-enables masks, acknowledges ISR/FH ISR, calls receive processing, records wait bits, and marks the controller broken on firmware/hardware fatal errors. A recovery kernel process periodically powers off, resets, boots firmware, and restores RX state when `broken` is set.
