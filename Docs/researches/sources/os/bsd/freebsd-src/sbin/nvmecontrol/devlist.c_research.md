# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/devlist.c

Implements `nvmecontrol devlist`, listing NVMe controllers and namespaces.

Key behaviors:
- Scans controller unit numbers `0..256`.
- Opens controller devices, reads controller data, and prints model number.
- For fabrics controllers, queries connection status and reconnect parameters to show connected transport/address or disconnected duration.
- Lists active namespaces by repeatedly reading the active namespace list.
- Computes namespace size from `nsze * sector_size`.
- Supports `--human`/`-h` for human-readable sizes.

Research notes:
- Uses connection-status ioctls when available but assumes local/non-fabrics controllers are connected if unsupported.
