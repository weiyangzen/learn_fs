# File Research: sources/os/plan9/plan9/sys/src/9/teg2/etherif.h

Ethernet controller interface header for the Tegra Plan 9 port.

Key contents:
- Defines `MaxEther` and number of packet type slots `Ntypes`.
- Defines `struct Ether`, embedding `ISAConf` and `Netif` plus controller callbacks and hardware state.
- Declares generic Ethernet helpers: `etheriq`, `addethercard`, `ethercrc`, and `parseether`.
- Defines circular ring helper macros `NEXT` and `PREV`.

Role:
- This is the contract between `devether.c` and individual Ethernet drivers such as `ether8169.c`.
- It standardizes callback names for attach, detach, transmit, interrupt, stats, control, power, and shutdown.

Notable constraints:
- Only four Ethernet controllers are supported by the fixed `MaxEther`.
