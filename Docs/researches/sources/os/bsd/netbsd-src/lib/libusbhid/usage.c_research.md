# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/usage.c

HID usage table loader and name/number conversion helpers.

Key responsibilities:
- Loads HID usage page data from `/usr/share/misc/usb_hid_usages` or caller-provided path.
- Parses page and in-page usage names, normalizing whitespace and dots to underscores.
- Stores dynamic arrays of usage pages and page contents.
- Converts usage page numbers to names with `hid_usage_page`.
- Converts full usage values to names with `hid_usage_in_page`.
- Supports wildcard/format entries where usage number is interpolated into a name.
- Parses names back to numeric page/usage values:
  - `hid_parse_usage_page`
  - `hid_parse_usage_in_page`
- Supports numeric `page:usage` fallback parsing in hexadecimal.

Role in subsystem:
- Human-readable HID usage name conversion layer for parsed descriptors and diagnostics.
