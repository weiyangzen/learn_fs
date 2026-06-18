# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bootprops.h

`bootprops.h` centralizes boot property names for network boot and iSCSI boot, including host/router/server properties, boot MAC, iSCSI target/initator data, CHAP fields, bootpath, and local MAC address.

It also declares kernel networking helper prototypes (`kdlifconfig`, `ksetifflags`, `kifioctl`) and iSCSI boot property structures for initiator, NIC, target, and combined boot state. Helper declarations load/free iSCSI properties and construct VHCI/physical boot paths.
