# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-print-json.c

## Role

`ocp-print-json.c` implements the JSON output backend for OCP log pages and OCP-specific persistent event log decoding. It converts packed OCP and NVMe payloads into json-c objects through nvme-cli JSON helper wrappers.

## Supported Logs

The backend supports JSON output for:

- hardware component log and component descriptions;
- firmware activation history;
- SMART extended log, with separate schema variants selected by output format version;
- telemetry parse output through `print_ocp_telemetry_json()`;
- C3 latency monitor log;
- C5 unsupported requirements log;
- C1 error recovery log;
- C4 device capabilities log;
- C9 telemetry string log;
- C7 TCG configuration log;
- persistent event log, including OCP TCG activity vendor-specific events.

## Formatting Strategy

The file uses a set of macros mapping concise names such as `obj_add_uint`, `obj_add_str`, and `array_add_obj` onto nvme-cli JSON helper functions. It allocates a root object per print operation, appends decoded fields, prints the object, and frees it when using the older `json_print_object()` path. Some helpers use `json_print()` instead.

Multi-byte numeric fields are converted with endian helpers such as `le16_to_cpu()`, `le32_to_cpu()`, `le64_to_cpu()`, `le128_to_cpu()`, and custom integer helpers such as `int48_to_long()` and `int56_to_long()`. GUIDs are usually printed by iterating bytes in reverse order or formatting two 64-bit halves.

## SMART Extended JSON

`json_smart_extended_log_v1()` emits human-label keys with spaces and historical names. `json_smart_extended_log_v2()` emits snake_case keys. Both decode the common SMART fields first, then use fallthrough switch cases based on `log_page_version` to include fields added in later OCP versions.

The dispatcher `json_smart_extended_log()` selects v1 by default and v2 when the caller passes output format version 2.

## Telemetry String Log JSON

`json_c9_log()` decodes the fixed C9 header, FIFO ASCII labels, reserved arrays, statistics identifier string table, event string table, VU event string table, and ASCII table. It computes table entry counts and byte offsets from device-provided start/size fields and copies table data from the full log buffer before constructing nested JSON objects.

## Persistent Event Log JSON

`json_persistent_event_log()` decodes the NVMe persistent event log header, then `json_pevent_entry()` iterates event entries with bounds checks against the caller-provided size. Standard event types delegate to nvme-cli JSON helpers. Vendor-specific events are checked with `ocp_is_tcg_activity_event()`; matching events are decoded as OCP TCG activity data.

## Notable Risks And Edge Cases

- Several fixed buffers are too small or suspicious for their intended text output. For example, C5 and C7 GUID buffers are declared `char guid_buf[GUID_LEN]` even though a 16-byte GUID needs at least 33 characters as hex plus NUL.
- C9 uses variable-length arrays sized from device-provided fields, so corrupt or malicious log data could drive large stack allocations.
- Some JSON object keys are repeated in loops, notably C4 DSSD power state descriptors, which can overwrite prior values depending on the JSON helper behavior.
- Several fields use `json_object_add_value_int()` for values that are wider than signed int, including some 64-bit or little-endian fields.
- Some casts read multi-byte values directly from byte arrays; this can be alignment-sensitive on stricter architectures.
- JSON schemas are inconsistent across logs and between SMART output versions, which matters for scripts consuming this plugin.
