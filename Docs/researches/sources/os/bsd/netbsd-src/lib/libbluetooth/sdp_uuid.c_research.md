# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_uuid.c

Defines the Bluetooth base UUID constant.

Key behavior:
- Exports `const uuid_t BLUETOOTH_BASE_UUID`.
- Value is `00000000-0000-1000-8000-00805f9b34fb`.

Dependencies:
- Public `sdp.h` and `<uuid.h>` type layout.
