# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry.c

Implements `parse-telemetry-log`, the Solidigm telemetry parser command.

Input modes:
- Reads telemetry from a device using libnvme.
- Or reads an offline binary with `--source-file`; in this mode a device path is rejected.

Options:
- `--host-generate`: 0 or 1, default 1.
- `--controller-init`: retrieve controller-initiated report.
- `--data-area`: 1 through 4; defaults to 3 when config is provided, otherwise 1.
- `--config-file`: JSON structure/config map for deep parsing.
- `--source-file`: telemetry binary file.
- `--jq-filter`: key in config containing a jq filter.

Main flow:
- Reads optional configuration JSON.
- Determines telemetry transfer size from identify data and calls `sldgm_dynamic_telemetry()`.
- Sets up `struct telemetry_log` with root JSON object, log pointer, log size, and configuration.
- Calls `solidigm_telemetry_log_data_areas_parse()`.
- Either prints full JSON or pipes root JSON through `jq -r '<filter>'`.

Risks/notes:
- The jq command is built with `snprintf("jq -r '%s'")` and executed via `popen()`, so filters from config are shell-interpreted.
- `read_file2buffer()` allocates exact file length and does not append NUL; JSON parsing depends on json-c accepting the buffer content.
