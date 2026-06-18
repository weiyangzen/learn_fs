# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/pci.h

This header defines PCI, PCI-X, and PCI Express FMA event subclass and payload names.

PCI event names:
- Base subclasses include `"pci"` and secondary `"sec"`.
- Common PCI events cover parity, SERR, master abort, target abort, delayed transaction timeout, target errors, and not responding.
- Payload fields include PCI status, command, secondary status, bridge control, and physical address.

PCI-X event names:
- Subclasses include `"pcix"` and secondary prefix `"sec-"`.
- Events cover ECC correctable/uncorrectable address/attribute/data errors, split transaction messages, split disabled/delayed/outstanding, and unexpected split.
- Payload fields include PCI-X status/command, bridge status, ECC control/status, and ECC attributes.

PCI Express event names:
- Base subclass is `"pciex"`.
- Events are grouped by physical/link/transaction/root-complex/bridge domains, including receiver/transition errors, bad DLLP/TLP, replay timeout, completion abort/timeout, ECRC, flow control protocol, malformed TLP, poisoned TLP, unsupported request, root-complex messages, and bridge secondary errors.
- Severity/class strings include correctable, fatal, nonfatal, no advertised error, and advisory nonfatal.
- Payload fields include device/link/root status, correctable/uncorrectable error status, severity, source id/validity, advanced control, and captured header dwords.

Other constants:
- `PCIEX_FABRIC` names a common fabric class.

Dependencies and relationships:
- Used by PCI bus nexus and device fault-management code.
- Complements platform-specific PCI headers such as `sun4_fire.h` and `sun4upci.h`.
