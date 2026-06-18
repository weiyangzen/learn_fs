# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/dump.c

Debug formatting and allocation helpers for the USB library.

Provides:
- `classname` mapping USB class IDs to readable names.
- `hexstr` heap-allocating byte dump string.
- `seprintiface` and `seprintconf` helpers for structured descriptor output.
- `Ufmt`, the `%U` formatter for `Dev*`, printing device path, class/subclass/proto, VID/DID, refs, strings, configurations, interfaces, endpoints, and device-specific descriptors.
- `estrdup` and `emallocz`, fatal-on-failure allocation wrappers with malloc tags.

Also defines global `usbdebug`.

This file is used heavily by discovery, driver startup, and diagnostics.
