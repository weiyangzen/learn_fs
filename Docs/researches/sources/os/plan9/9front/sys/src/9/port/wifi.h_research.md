# File Research: sources/os/plan9/9front/sys/src/9/port/wifi.h

Shared Wi-Fi data structures and prototypes.

Key responsibilities:
- Defines `Wkey`, `Wnode`, `Wifi`, and `Wifipkt`.
- Defines ESSID length, cipher identifiers (`TKIP`, `CCMP`), and the block timestamp flag.
- Captures per-node association, beacon, rate, RSN, key, and statistics state.
- Captures per-interface state: attached `Ether`, crypt lock, input queue, target BSSID/ESSID, supported rates, active BSS, node cache, and driver transmit hook.
- Declares public helper functions used by concrete Wi-Fi NIC drivers.

Dependencies:
- Relies on Plan 9 Ethernet address sizes, `Ether`, `Queue`, `Block`, `Ref`, and kernel synchronization types.
