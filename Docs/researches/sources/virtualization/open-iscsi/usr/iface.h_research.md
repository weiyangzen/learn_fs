# File Research: sources/virtualization/open-iscsi/usr/iface.h

This header declares the iface management API and iface config directory for open-iscsi.

Key contents:
- `IFACE_CONFIG_DIR`, pointing to `ISCSI_DB_ROOT"/ifaces"`.
- Forward declarations for `struct iface_rec`, `struct list_head`, and `struct boot_context`.
- APIs for copying, matching, allocating, reading, defaulting, validating, writing, updating, deleting, enumerating, and linking iface records.
- Binding predicates for hardware address, netdev, and IP address.
- Printing helpers for tree and flat iface output.
- Boot-context helpers for deriving iface records from firmware boot metadata.
- Kernel net-config helpers:
  - `iface_get_param_count()`
  - `iface_build_net_config()`
  - `iface_get_iptype()`
- `iface_fmt` and `iface_str()` logging macros for consistent iface log formatting.

Important dependencies:
- Includes `libopeniscsiusr/libopeniscsiusr.h` for `struct iscsi_iface` and iface type definitions.
- Includes `<sys/uio.h>` for iovec-based netlink parameter construction.

Filesystem/storage relevance:
- This header exposes the interface binding layer used by session login and offload setup, which directly affects how iSCSI-backed block devices are reached.
