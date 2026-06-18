# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/data.c

Packed HID report data extraction and insertion.

Key responsibilities:
- `hid_get_data`:
  - extracts a field from a byte buffer using `hid_item_t.pos` and `report_size`,
  - handles little-endian bit packing,
  - masks to field width,
  - sign-extends when logical minimum is negative.
- `hid_set_data`:
  - masks input data to report size,
  - shifts it into bit position,
  - updates only the target field bits in the report buffer.

Role in subsystem:
- Converts between parsed HID item metadata and concrete report payload bits.
