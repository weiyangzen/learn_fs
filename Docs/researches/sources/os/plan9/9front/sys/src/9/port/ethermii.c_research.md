# File Research: sources/os/plan9/9front/sys/src/9/port/ethermii.c

Implements generic MII/PHY support for Ethernet drivers. It probes PHYs, creates `MiiPhy` records, reads/writes PHY registers with optional paged register handling, resets PHYs, configures autonegotiation, and computes link status.

`mii` probes a mask of possible PHY addresses and records valid OUIs. `miimir`/`miimiw` serialize register access and apply `pagereg` mapping. `miiane` advertises 10/100/1000 capabilities and pause support, then restarts autonegotiation. `miianec45`, `miimmdr`, and `miimmdw` support MMD/Clause-45 style multi-gigabit autonegotiation registers.

`miistatus` reads status twice for sticky link state, determines negotiated speed/duplex/flow-control, and sets `phy->link`. `miistatusc45` handles 2.5G/5G/10G MMD status bits.
