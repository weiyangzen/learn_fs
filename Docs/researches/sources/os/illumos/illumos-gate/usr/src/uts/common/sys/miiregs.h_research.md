# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/miiregs.h

Purpose: Defines MII register addresses, bit masks, auto-negotiation fields, 1000Base-T master/slave fields, extended status bits, and known PHY OUIs/models.

Key definitions:
- Standard register indexes: control, status, PHY IDs, auto-negotiation, master/slave, extended status, vendor space.
- Control bits: reset, loopback, speed, auto-negotiation, powerdown, isolate, restart AN, full duplex, gigabit.
- Status and ability bits for 10/100/1000 speeds, full/half duplex, pause/asymmetric pause.
- PHY ID extraction macros: `MII_PHY_MFG()`, `MII_PHY_MODEL()`, `MII_PHY_REV()`.
- Manufacturer OUI and model constants for common PHY vendors.

Important detail: This is a constants-only companion to the MII framework.

Relevance to subset A: Network PHY support, outside filesystem focus.
