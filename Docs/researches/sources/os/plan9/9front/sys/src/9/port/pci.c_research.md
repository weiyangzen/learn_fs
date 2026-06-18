# File Research: sources/os/plan9/9front/sys/src/9/port/pci.c

Portable PCI discovery, configuration-space access wrappers, BAR sizing/mapping, capability handling, MSI, and power management.

Key responsibilities:
- Provides `%T` formatting for TBDF bus identifiers.
- Allocates and tracks global PCI device lists and bridge children.
- Serializes architecture PCI config reads/writes with `pcicfglock` and `pciparentdev`.
- Sizes BARs and ROM BARs by writing all ones and restoring original values.
- Recursively scans PCI buses, discovers multifunction devices, PCI-PCI bridges, CardBus bridges, and BARs.
- Validates BAR/window ranges against parent bridge windows and clears invalid mappings.
- Allocates bridge windows and BAR addresses with `pcibusmap()` and computes sizing with `pcibussize()`.
- Provides matching helpers by VID/DID or TBDF.
- Dumps PCI hierarchy and resets/disables devices.
- Manipulates command bits: I/O enable, bus master, memory-write-invalidate.
- Enumerates capabilities, including MSI, MSI-X disable, HyperTransport matching, and power management.
- Enables/disables MSI and restores devices from power states in `pcienable()`.

Important behavior:
- `pcienable()` recursively enables parent bridges before a device.
- D3 wake restores saved BARs, interrupt line, latency, cache line size, and command register.
- Bridge scans initialize secondary/subordinate buses when firmware left them zero.
- `pcidisable()` disables MSI/MSI-X and bus mastering but leaves many resources intact.

Notable risks:
- `pcidevfree()` detaches from lists but comments that memory is leaked.
- BAR/window validation and allocation are sensitive to 32-bit vs 64-bit/prefetchable flag encodings.
