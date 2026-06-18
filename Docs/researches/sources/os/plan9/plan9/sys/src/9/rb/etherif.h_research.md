# File Research: sources/os/plan9/plan9/sys/src/9/rb/etherif.h

RouterBOARD Ethernet interface declarations.

Key contents:
- Defines `MaxEther=2` and `Ntypes=8`.
- Defines `Ether` controller structure with hardware fields, queue, MAC address, optional driver callbacks, and embedded `Netif`.
- Declares `etheriq`, `addethercard`, `ethercrc`, and `parseether`.
- Provides ring index helper macros `NEXT` and `PREV`.

Role:
- Shared contract between Ethernet device code and any controller-specific drivers.

Notable risks:
- Callback fields are guarded by `MULTIETHERTYPES`; this port’s `devether.c` mostly provides a single built-in controller path.
