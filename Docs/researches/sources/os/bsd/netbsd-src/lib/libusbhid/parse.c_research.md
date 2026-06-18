# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/parse.c

USB HID report descriptor parser.

Key responsibilities:
- Maintains parser state in `struct hid_data`, including:
  - descriptor cursor,
  - current item state,
  - usage list,
  - report kind positions,
  - report ID filter,
  - saved collection item.
- Parses HID short and long items.
- Handles HID main items:
  - input,
  - output,
  - feature,
  - collection,
  - end collection.
- Handles global items:
  - usage page,
  - logical/physical min/max,
  - unit exponent/unit,
  - report size,
  - report ID,
  - report count,
  - push/pop state.
- Handles local items:
  - usage,
  - usage min/max,
  - designator fields,
  - string fields,
  - delimiter.
- Expands variable items with report count into individual `hid_item_t` outputs.
- Tracks absolute bit positions separately for input, output, and feature reports.
- Filters by report ID in `hid_get_item`.

Public functions:
- `hid_start_parse`
- `hid_end_parse`
- `hid_get_item`
- `hid_report_size`
- `hid_locate`

Role in subsystem:
- Core parser translating raw HID descriptors into typed item metadata for consumers.
