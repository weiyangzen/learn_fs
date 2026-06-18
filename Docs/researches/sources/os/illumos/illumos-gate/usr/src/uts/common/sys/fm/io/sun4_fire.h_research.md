# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/sun4_fire.h

This header defines FMA event and payload names for sun4 Fire/Oberon PCI Express platform components.

Top-level platform names:
- `PCIEX_FIRE` is `"fire"`.
- `PCIEX_OBERON` is `"oberon"`.

Ereport domains:
- JBC errors for JBus bridge conditions such as parity, timeout, illegal access, unsolicited read/interrupt, and EBus timeout.
- UBC errors for Oberon DMA/memory/PIO read/write UE/AXA cases.
- DMC errors for MSI, message, event queue, bypass, translation, TTE, TBW, and TTC failures.
- PEC errors for internal header buffers, unsupported/completion/protocol conditions, link state changes, PCIe transaction/link errors, and uncorrectable buffer/header/data cases.

Payload fields:
- Primary-error marker.
- PEC payload register fields for ILU and TLU error log/status/enable/capture headers.
- DMC payload fields for IMU/MMU register state and fault address/status.
- JBC payload fields for DMC/JBus register state and logs.
- UBC payload fields for error logs, unum/resource, device id, and CPU vector.

Dependencies and relationships:
- Platform-specific supplement to generic PCIe FMA names in `sys/fm/io/pci.h`.
- Used by Fire/Oberon nexus fault-reporting code to keep emitted nvlist names stable.
