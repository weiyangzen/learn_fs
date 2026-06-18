# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/wsconsctl.c

Main program for `wsconsctl`.

Key behavior:
- Defines the device-type switch table for keyboard, mouse, and display, including field tables and get/put/enumeration callbacks.
- Supports `-a` for all auto-printable fields, `-f file` to force a device node, `-n` to suppress separators, and compatibility `-w`.
- Without args, defaults to `-a`.
- Opens devices read-write when possible, otherwise read-only.
- For set operations, parses `name=value`, `name+=value`, and `name-=value`.
- For modify/init fields, reads current state before applying a change.
- Writes one field at a time, optionally reads back, and prints resulting values unless suppressed by flags.
- `tab_by_name()` parses optional numeric device suffixes like `mouse1.param`.

Filesystem/OS relevance:
- Command dispatcher for wscons device control.
- Shows field-driven ioctl orchestration and multi-device enumeration under `/dev`.
