# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/devices.c

## Purpose
Tracks RDMA devices capable of SMBDirect and provides netdev-to-RDMA capability lookup for client/server upper layers.

## Device Registration
- `smbdirect_ib_device_rdma_capable_node_type()` accepts only devices with FRWR support and node type `RDMA_NODE_IB_CA` or `RDMA_NODE_RNIC`.
- `smbdirect_ib_client_add()` logs device capabilities, ignores unsupported devices, allocates `struct smbdirect_device`, stores `ib_dev` and a copy of its name, and inserts it into the global list.
- `smbdirect_ib_client_remove()` removes matching device entries and frees them.
- `smbdirect_ib_client_rename()` updates stored names for diagnostic consistency.
- `smbdirect_ib_client` is the RDMA core client with add/remove/rename callbacks.

## Netdev Lookup
- `smbdirect_netdev_find_rdma_capable_node_type()` scans registered devices and ports, comparing `ib_device_get_netdev()` output to the given netdev.
- If not found in the local list, it falls back to `ib_device_get_by_netdev()`.
- `smbdirect_netdev_rdma_capable_node_type()` additionally checks bridge/VLAN lower devices and treats IPoIB netdevs as `RDMA_NODE_IB_CA`.

## Init/Exit
- `smbdirect_devices_init()` initializes global rwlock/list and registers the IB client.
- `smbdirect_devices_exit()` clears tracked devices under lock, then unregisters the IB client.

## Concurrency
- Global device list uses `smbdirect_globals.devices.lock` as an rwlock.
- Netdev refs obtained from RDMA helpers are released with `dev_put()`.
