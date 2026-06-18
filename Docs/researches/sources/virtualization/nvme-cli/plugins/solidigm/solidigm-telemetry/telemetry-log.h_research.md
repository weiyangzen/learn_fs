# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-telemetry/telemetry-log.h

Defines shared telemetry parser state.

Key definitions:
- `SOLIDIGM_LOG_WARNING()` stderr logging macro.
- `MEMBER_SIZE()` helper.
- `struct telemetry_log` with:
  - raw `nvme_telemetry_log *log`
  - `log_size`
  - root JSON object
  - optional configuration JSON
  - `is_ocp`
  - `skhT_offset`

Also maps `static_assert` to `_Static_assert` for C builds.
