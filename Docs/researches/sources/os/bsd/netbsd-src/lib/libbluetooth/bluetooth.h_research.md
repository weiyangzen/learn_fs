# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/bluetooth.h

Public Bluetooth library header.

Key behavior:
- Declares host/protocol lookup APIs, address conversion APIs, HCI device APIs, and bthcid PIN packet structures.
- Defines `struct bt_devinfo`, `struct bt_devreq`, `struct bt_devfilter`, and `struct bt_devinquiry`.
- Defines `BTOPT_DIRECTION` and `BTOPT_TIMESTAMP` flags for `bt_devopen`.
- Defines `bt_devclose(s)` as `close(s)`.
- Declares filter bit manipulation helpers and inquiry/device enumeration entry points.
- Defines packed PIN request/response structs for bthcid interaction and default socket `/var/run/bthcid`.
- Under `COMPAT_BLUEZ`, provides BlueZ-style address and endian macros.

Dependencies:
- NetBSD Bluetooth kernel headers: `netbt/bluetooth.h`, `netbt/hci.h`, and `netbt/l2cap.h`.
- `<netdb.h>`, `<stdio.h>`, and `<time.h>`.

Notes:
- Consumers using `bt_devclose` must include or otherwise see `close`.
