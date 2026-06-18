# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ndi_impldefs.h

Internal Nexus Driver Interface implementation definitions.

Key responsibilities:
- Defines `struct ndi_event_hdl`, the internal event callback-management handle with owning devinfo, handle/event mutexes, callback-list mutex, interrupt block cookie, priority-level counters, event-cookie list, and next-handle link.
- Declares property encoding/decoding and common update/lookup/remove helpers for bytes, ints, int64, strings, and string arrays.
- Declares internal node configuration and unconfiguration routines.
- Retains obsolete device-tree change block/allow interfaces for driver compatibility.
- Declares framework-only helpers for auto-assigned node IDs, node class, node attributes, explicit node ID setting, and driver.conf child creation.

Dependencies:
- Includes core DDI/devinfo, properties, mutex, page, autoconf, and implementation headers.

Notable risks:
- This is internal DDI framework surface; consumers should not treat it as stable public driver ABI.
- Event handle locking is split between event definitions and callback lists, so call paths must use the correct mutex.
