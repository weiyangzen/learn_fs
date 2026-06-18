# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/kb/hid.c

Minimal HID report descriptor/parser support used by USB pointer handling.

Core logic:
- `get8bits` and `getbits` extract unaligned bitfields from a `Chain`.
- `parsereportdesc` walks a HID report descriptor and builds a compact `HidRepTempl` focused on pointer reports: buttons, X, Y, Z/padding, and wheel fields.
- Tracks report ID, report size/count, usage page, usages, input blocks, and collections.
- Requires a pointer application with X/Y and buttons; otherwise reports descriptor rejection.
- `parsereport` decodes one input report into per-interface values and sign-extends X/Y/wheel fields.
- `hidifcval` returns the nth decoded value of a requested kind.
- `dumpreport` prints decoded template/value state for debugging.

Scope is intentionally narrow: it is not a full HID parser, but enough for common mouse report descriptors.
