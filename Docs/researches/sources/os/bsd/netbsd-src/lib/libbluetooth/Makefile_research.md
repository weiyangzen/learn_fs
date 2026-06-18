# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/Makefile

Builds NetBSD `libbluetooth`.

Key behavior:
- Enables `_FORTIFY_SOURCE` by default for a network protocol library.
- Builds Bluetooth address/protocol helpers, HCI device helpers, SDP data helpers, SDP service/session/record helpers, and UUID support.
- Adds `sdp_compat.c` unless `SDP_COMPAT=no`.
- Installs public headers `bluetooth.h` and `sdp.h` to `/usr/include`.
- Installs manpages and extensive MLINK aliases for Bluetooth host/protocol/device and SDP APIs.
- Adds the current directory to `CPPFLAGS`.

Dependencies:
- NetBSD `bsd.lib.mk`.
- Kernel Bluetooth headers and SDP implementation files.
