# File Research: sources/os/plan9/9front/sys/src/9/port/pci.h

PCI constants, `Pcidev` structure, and public PCI helper prototypes.

Key contents:
- Defines PCI header offsets for type 0, type 1, and type 2 headers.
- Defines common class/subclass codes, capability IDs, BAR flags, and command-register bits.
- Defines `Pcidev` with TBDF, IDs/class fields, interrupt line, BAR/ROM/window resources, parent/bridge links, and cached capability offsets.
- Lists selected vendor IDs.
- Declares config-space access, scan/map/match, BAR, interrupt, command-bit, capability, MSI, power, enable/disable, and inventory functions.
- Defines bus type constants and TBDF encoding/decoding macros.
- Registers `%T` vararg formatting.

Role:
- Shared public interface between architecture PCI access code, portable PCI core, and PCI device drivers.
