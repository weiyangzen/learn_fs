# File Research: sources/os/bsd/openbsd-src/sys/sys/sockio.h

Socket and network-interface ioctl command namespace.

This header defines ioctl numbers for socket process-group and out-of-band mark operations, interface address/flag/metric/media/MTU/configuration operations, multicast, tunnel, bridge, VLAN, MPLS, pflow, pfsync, carp, MBIM, and many interface-specific control surfaces. It uses `_IO*` macros from `<sys/ioccom.h>` and references request structures defined by networking headers.

The file is pure ABI constant definition; it does not define the request structs themselves.

Filesystem/storage relevance: mostly network-facing. It matters to VFS only through the generic `ioctl(2)` dispatch on file descriptors and special device/socket descriptor handling.
