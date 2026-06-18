# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/bt_dev.c

Implements raw HCI Bluetooth device access helpers.

Key behavior:
- `bt_devaddr` maps a device name or address string to a live device address, requiring `BTF_UP`.
- `bt_devname` maps an address to a live device name with `SIOCGBTINFOA`.
- `bt_devopen` opens a raw HCI socket, optionally enables packet direction/timestamp ancillary data, binds to the selected local address, and connects when a name is supplied.
- `bt_devsend` writes an HCI command packet header plus parameters using `writev`.
- `bt_devrecv` optionally waits with `kqueue`, receives one packet, and validates complete HCI command/ACL/SCO/event packet lengths.
- `bt_devreq` temporarily installs a command-complete/status/event filter, sends a command, waits for a matching response, copies response payload, then restores the old filter.
- Filter helpers wrap `SO_HCI_PKT_FILTER` and `SO_HCI_EVT_FILTER`.
- `bt_devinquiry` opens a controller, issues general inquiry, parses standard, RSSI, and extended inquiry results, deduplicates by address, and returns a calloc-allocated result array.
- `bt_devinfo` and `bt_devenum` expose controller information, features, stats, and enumeration callbacks.

Dependencies:
- Raw Bluetooth HCI sockets, HCI ioctl requests, kqueue, and NetBSD HCI packet structures.

Notes and risks:
- `bt_devinquiry` stores the first active device name into the packet buffer via an internal callback when no device name is supplied.
- Result arrays returned by `bt_devinquiry` must be freed by the caller.
- `bt_devreq` restores filters best-effort even after request failure.
