# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/descr.c

HID report descriptor acquisition and ownership helpers.

Key responsibilities:
- `hid_get_report_desc`:
  - uses `USB_GET_REPORT_DESC` ioctl on a USB HID device fd,
  - wraps returned descriptor data into a `report_desc_t`.
- `hid_use_report_desc`:
  - allocates a descriptor object and copies caller-provided bytes.
- `hid_dispose_report_desc`:
  - frees descriptor storage.

Role in subsystem:
- Provides the descriptor object consumed by the parser in `parse.c`.
