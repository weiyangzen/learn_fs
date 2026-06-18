# File Research: sources/os/plan9/plan9/sys/src/9/teg2/devether.c

Generic Plan 9 Ethernet device (`#l`) for Tegra, bridging controller drivers into the `netif` framework.

Key responsibilities:
- Manages an array of discovered `Ether` devices and exposes them through Plan 9 channel operations.
- Delegates walk/stat/open/close/read/write to `netif` helpers.
- Provides receive fanout through `etheriq`, including multicast filtering, promiscuous listeners, bridge suppression, header-only tracing, and copy avoidance for one consumer.
- Provides transmit queueing through `etheroq`, including loopback/broadcast/promiscuous local delivery.
- Registers controller reset functions through `addethercard`.
- Parses Ethernet addresses and computes Ethernet CRC.
- Resets/probes Ethernet controllers by combining `archether`, `isaconfig`, registered card types, address overrides, interrupt hookup, and `netifinit`.
- Calls controller shutdown hooks during device shutdown.

Important behavior:
- Output queue size scales with link speed: larger for gigabit controllers.
- Control writes support `nonblocking` locally before passing unknown commands to controller-specific `ctl`.
- `etherread` lets controller `ifstat` refresh hardware counters for both `ifstats` and normal `stats`.

Dependencies and assumptions:
- Depends on `etherif.h`, `netif.h`, board `archether`, and controller drivers such as RTL8169.
- Expects controller drivers to fill callbacks such as `attach`, `transmit`, `interrupt`, `ifstat`, `promiscuous`, `multicast`, and `shutdown`.

Notable risks:
- Only `MaxEther` controllers can be registered.
- Loopback delivery calls `etheriq` at high interrupt priority.
