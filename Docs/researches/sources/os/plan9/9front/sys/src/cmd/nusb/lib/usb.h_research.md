# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/lib/usb.h

This header is the central nusb USB library interface. It defines descriptor constants, standard request constants, USB class codes, endpoint direction/type constants, configuration attributes, HID report tag constants, and tunable limits for endpoints, configurations, interfaces, raw descriptors, and control-request retries.

The core structures are `Dev`, `Usbdev`, `Ep`, `Iface`, `Conf`, `Desc`, and unpacked standard descriptor layouts. `Dev` represents endpoint-zero devices or opened endpoints, with fds, parsed USB tree, endpoint pointer, refcount, and driver auxiliary pointer. `Usbdev` stores device-level identity, strings, configurations, endpoint chains, and raw device-specific descriptors. `Ep`, `Iface`, and `Conf` represent parsed topology and alternate settings.

The header provides little-endian `GET2`/`PUT2`/`GET4`/`PUT4` macros, CSP packing/unpacking macros, debug-print macros, vararg annotations, and declarations for descriptor parsing, device opening/configuration, endpoint opening, control transfers, unstalling, alt/config selection, allocation helpers, class-name formatting, and the `%U` formatter.

All driver subtrees in this group depend on this header for USB request construction, descriptor interpretation, endpoint selection, and common object lifetimes.
