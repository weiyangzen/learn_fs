# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/bluetooth.c

Implements Bluetooth address, host database, and protocol database helpers.

Key behavior:
- Reads host entries from `/etc/bluetooth/hosts`.
- Reads protocol entries from `/etc/bluetooth/protocols`.
- Provides `bt_gethostbyname`, `bt_gethostbyaddr`, `bt_gethostent`, `bt_sethostent`, and `bt_endhostent`.
- Provides `bt_getprotobyname`, `bt_getprotobynumber`, `bt_getprotoent`, `bt_setprotoent`, and `bt_endprotoent`.
- Parses whitespace-separated files, skips comments, and stores aliases in fixed arrays of 35 entries.
- `bt_ntoa` formats `bdaddr_t` as six colon-separated bytes in display order.
- `bt_aton` parses one- or two-hex-digit colon-separated address components into `bdaddr_t`.

Dependencies:
- Public `bluetooth.h`, `<netdb.h>`, and standard file/string APIs.

Notes and risks:
- Uses static global buffers and result structs, so these APIs are not reentrant.
- `bt_endprotoent` always closes `protof`; it ignores `proto_stayopen`, unlike host handling.
