# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/xs_wire.h

Imported Xen public XenStore wire protocol ABI.

Purpose:
- Defines the socket/shared-ring protocol between XenStore daemon and client libraries or guest kernels.

Key content:
- Defines `enum xsd_sockmsg_type` for debug, directory, read/write, perms, watch/unwatch, transactions, introduce/release, domain path, mkdir/rm, watch event, error, resume, set target, restrict, and reset watches.
- Defines write mode strings.
- Optionally defines errno-to-string mapping table when errno constants are available.
- Defines `struct xsd_sockmsg` header with type, request ID, transaction ID, and payload length.
- Defines watch tuple type enum.
- Defines `XENSTORE_RING_SIZE`, ring index type/mask, and `struct xenstore_domain_interface` with request/response rings and producer/consumer indexes.
- Defines payload and path maximums.

Integration:
- Directly used by 9front’s `devxenstore.c` XenStore device/client implementation.
- XenStore is used by xenbus setup for block/network devices and shutdown watches.
- Mapped from Xen start info at the fixed `XENBUS` virtual address in this port.

Risks/notes:
- The comment warns that violating `XENSTORE_PAYLOAD_MAX` is severe.
- Concurrent request/response matching depends on request IDs and ring ordering.
