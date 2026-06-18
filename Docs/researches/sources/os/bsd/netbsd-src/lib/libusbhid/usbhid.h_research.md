# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/usbhid.h

Public API header for `libusbhid`.

Key contents:
- Declares opaque descriptor/parser types:
  - `report_desc_t`
  - `hid_data_t`
- Defines `hid_kind_t`:
  - input,
  - output,
  - feature,
  - collection,
  - endcollection.
- Defines `hid_item_t`, containing:
  - HID global fields,
  - HID local fields,
  - collection metadata,
  - item kind,
  - flags,
  - absolute bit position,
  - parser stack linkage.
- Defines usage helpers:
  - `HID_PAGE`
  - `HID_USAGE`
- Declares descriptor APIs:
  - `hid_get_report_desc`
  - `hid_use_report_desc`
  - `hid_dispose_report_desc`
- Declares parser APIs:
  - `hid_start_parse`
  - `hid_end_parse`
  - `hid_get_item`
  - `hid_report_size`
  - `hid_locate`
- Declares usage-name APIs.
- Declares report field data APIs:
  - `hid_get_data`
  - `hid_set_data`

Role in subsystem:
- Public contract for reading, parsing, inspecting, and manipulating USB HID reports.
