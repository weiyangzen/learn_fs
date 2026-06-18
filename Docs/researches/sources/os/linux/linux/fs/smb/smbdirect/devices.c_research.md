# File Research: sources/os/linux/linux/fs/smb/smbdirect/devices.c

Tracks RDMA-capable IB devices usable for SMB Direct and provides netdev-to-RDMA-capability discovery.

Key functions:
- `smbdirect_ib_device_rdma_capable_node_type()` accepts only devices with FRWR support and node type `RDMA_NODE_IB_CA` or `RDMA_NODE_RNIC`.
- `smbdirect_ib_client_add()` logs device capabilities, logs per-port protocol support, allocates a `smbdirect_device`, copies the IB device name, and adds it to the global device list.
- `smbdirect_ib_client_remove()` removes matching tracked devices and frees their records.
- `smbdirect_ib_client_rename()` updates the cached device name for diagnostic logging.
- `smbdirect_netdev_find_rdma_capable_node_type()` searches tracked devices and ports for a matching netdev via `ib_device_get_netdev()`, then falls back to `ib_device_get_by_netdev()`.
- `smbdirect_netdev_rdma_capable_node_type()` checks the given netdev, bridge/VLAN lower devices, and IPoIB type to return `RDMA_NODE_RNIC`, `RDMA_NODE_IB_CA`, or `RDMA_NODE_UNSPECIFIED`.
- `smbdirect_devices_init()` initializes the global device list lock and registers the IB client.
- `smbdirect_devices_exit()` frees tracked device records and unregisters the IB client.

Important state:
- Uses `smbdirect_globals.devices.list` protected by `rwlock_t`.
- Device records keep both `ib_dev` and a cached `ib_name` so removals/renames can log stable names.

Dependencies:
- Requires `smbdirect_frwr_is_supported()` from `socket.c`.
- Uses RDMA device, port, and netdev lookup APIs.
- Exported capability lookup is `smbdirect_netdev_rdma_capable_node_type()`.

Maintenance notes:
- Netdev lookup correctly drops references from `ib_device_get_netdev()` with `dev_put()`.
- Exit deliberately clears the list before `ib_unregister_client()` so normal remove callbacks do not produce removal logs during module unload.
