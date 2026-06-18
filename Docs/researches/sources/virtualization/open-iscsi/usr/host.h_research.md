# File Research: sources/virtualization/open-iscsi/usr/host.h

Public header for iSCSI host helpers. It includes libopeniscsiusr, local type/config definitions, and declares the host information and CHAP configuration APIs.

It defines host-related constants: `MAX_HOST_NO`, CHAP table size limit, CHAP buffer size, and request buffer size including `struct iscsi_uevent`.

`struct host_info` combines an `iface_rec` with a `host_no`. Exported functions are `host_info_print()` for CLI-style host/session output and `chap_build_config()` for turning an `iscsi_chap_rec` into netlink iovecs.
