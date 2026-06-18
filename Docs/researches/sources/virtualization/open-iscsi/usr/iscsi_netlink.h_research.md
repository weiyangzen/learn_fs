# File Research: sources/virtualization/open-iscsi/usr/iscsi_netlink.h

This header defines small netlink attribute helpers for open-iscsi.

Key contents:
- Includes Linux netlink definitions.
- Defines alignment/data/length macros:
  - `ISCSI_NLA_HDRLEN`
  - `ISCSI_NLA_DATA(nla)`
  - `ISCSI_NLA_LEN(len)`
  - `ISCSI_NLA_TOTAL_LEN(len)`
- Declares `iscsi_nla_alloc(uint16_t type, uint16_t len)`.

Important dependencies:
- Uses `struct nlattr` and `NLA_ALIGN()` from `<linux/netlink.h>`.
- Forward-declares `struct iovec`.

Filesystem/storage relevance:
- Supports construction of netlink payloads used to configure iSCSI kernel/session/iface parameters, particularly in `iface.c`.

Notable constraints:
- This header only declares allocation and macros; ownership/freeing behavior is determined by callers and the implementation of `iscsi_nla_alloc()`.
