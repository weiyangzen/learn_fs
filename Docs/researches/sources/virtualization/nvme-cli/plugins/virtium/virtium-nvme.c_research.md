# File Research: sources/virtualization/nvme-cli/plugins/virtium/virtium-nvme.c

Implements Virtium `save-smart-to-vtview-log` and `show-identify`.

SMART/vtView logging:
- Builds a session header containing test name, timestamp, identify controller data, and firmware slot data encoded as hex.
- Periodically appends SMART records in semicolon-delimited form.
- Includes capacity, critical warning, temperature, spare values, percentage used, 128-bit counters, thermal counters, and sensor temperatures.
- Auto-generates default filename `./vtView-Smart-log-YYYY-MM-DD.txt`.

Options:
- `--run-time` hours, default 20.
- `--freq` hours, default 10.
- `--output-file`.
- `--test-name`.

Identify display:
- Fetches identify controller data.
- Prints a JSON-like detailed breakdown with raw hex fields and explanatory bit text.
- Dumps power state descriptors and vendor-specific identify region.

Important helpers:
- `vt_convert_data_buffer_to_hex_string()` converts buffers to hex, optionally reversed.
- `vt_process_string()` trims trailing spaces.
- `vt_parse_detail_identify()` prints many NVMe identify fields and capability bit descriptions.

Risks/notes:
- Output is manually constructed with `printf()` and may not always be strict JSON.
- Uses many `strcat()` calls into fixed-size buffers.
- `vt_update_vtview_log_header()` checks `strlen(path) > sizeof(header.path)` but exact-size strings still overflow with NUL.
