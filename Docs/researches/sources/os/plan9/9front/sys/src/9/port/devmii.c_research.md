# File Research: sources/os/plan9/9front/sys/src/9/port/devmii.c

Purpose: Ethernet MII/SMI/MDIO PHY debug device `#Φ`, exposing registered MII buses and PHY registers.

Exposed interface: `#Φ/<bus>/<phy>/ctl`, `mii`, and `mmd`. `ctl` reads PHY status/dump and accepts `reset`, `status`, and `autoneg`. `mii` reads/writes Clause 22 16-bit registers; `mmd` reads/writes Clause 45 device/register space.

Core implementation: `linkage` installs `addmiibus` and `delmiibus` callbacks. `addbus`/`delbus` maintain a locked bus table keyed by pointer or name. `miigen` builds the bus/phy/register-file hierarchy. `getphy` validates qid-derived bus and PHY. `phystatus` emits id, OUI, link, speed, duplex, and a register dump.

Register I/O: `miiread` and `miiwrite` require exact two-byte accesses, enforce offset ranges, convert little-endian 16-bit values, and call `miimir`/`miimiw` or `miimmdr`/`miimmdw`.

Dependencies: `ethermii.h` MII structures and functions.

Research notes: review should focus on offset masking/range checks, byte-order expectations for register files, bus table lifetime vs driver removal, and privilege expectations because files are mode `0600`.
