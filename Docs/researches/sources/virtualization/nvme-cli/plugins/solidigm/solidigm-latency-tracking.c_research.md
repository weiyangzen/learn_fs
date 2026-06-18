# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-latency-tracking.c

Implements the Solidigm `latency-tracking-log` command. It can enable/disable feature ID `0xe2`, query whether latency tracking is enabled, or fetch read/write latency log pages `0xc1`/`0xc2`.

Key structures:
- `latency_statistics` stores version fields, up to 1216 buckets, and optional average latency.
- `latency_tracker` carries the libnvme handle, Solidigm UUID index, parsed CLI config, output mode, and bucket parsing state.

Main flow:
- `solidigm_get_latency_tracking_log()` parses `--enable`, `--disable`, `--read`, `--write`, and `--type`.
- It validates output format, log type range `0..0xf`, and Solidigm UUID index.
- `latency_tracking_enable()` performs `nvme_set_features()` for feature `0xe2`.
- `latency_tracker_get_log()` builds a Get Log command, encodes log-specific type into CDW10 LSP and UUID index into CDW14, then prints raw, normal, or JSON output.
- Without read/write/enable/disable options, it queries the feature via `nvme_get_features()`.

Parsing behavior:
- Revision 3 uses fixed linear ranges with different microsecond steps and only prints nonzero tail ranges for final sections.
- Revision 4 uses logarithmic bucket position calculation via `latency_tracker_bucket_pos2us()`.
- Version 4.0 uses 152 buckets and base range bits 3; newer v4 defaults to 1216 buckets and base range bits 6.
- Version 4.8+ exposes `average_latency`.

Output:
- Normal output is tabular with bucket id, start, end, and value.
- JSON output emits `{ "latstats": { "type": ..., "average_latency": ..., "values": [...] } }`.
- Binary output dumps the raw `latency_statistics` buffer.

Risks/notes:
- `latency_tracker_post_parse()` runs even for unsupported revisions, so JSON mode may create an empty `latstats` if pre-parse was not called and `bucket_list` is unset.
- Log data is read into the maximum struct size regardless of actual revision.
