# File Research: sources/virtualization/nvme-cli/plugins/solidigm/solidigm-log-page-dir.c

Implements Solidigm `log-page-directory`, which lists supported standard, Solidigm vendor-specific, and OCP log pages.

Main behavior:
- Fetches Supported Log Pages log `NVME_LOG_LID_SUPPORTED_LOG_PAGES` for UUID index 0.
- If UUID list is unavailable, it assumes vendor logs at UUID index 0 are Solidigm logs.
- If UUID list is available, it finds Solidigm and OCP UUID indexes and fetches supported log pages for each.
- Emits either normal table output or JSON array output.

Important helpers:
- `init_lid_dir()` initializes all LIDs as unsupported and named `"Unknown"`.
- `get_standard_lids()` maps standard LIDs through `nvme_log_to_string()`.
- `get_solidigm_lids()` names Solidigm LIDs such as `0xc1` read latency, `0xc2` write latency, `0xdd` marketing log, `0xf9` workload tracker, and `0xfe` SK SMART/outlier log.
- `get_ocp_lids()` names OCP vendor LIDs.
- `update_vendor_lid_supported()` marks only vendor LIDs `>= 0xc0`.

Output:
- Normal: columns `uuidx`, `LID`, `Description`.
- JSON: array of `{ uuidx, lid, description }`.

Risks/notes:
- Tracks only UUID indexes `0..2` via `SOLIDIGM_MAX_UUID`.
- Uses static `lid_dir` objects, so returned directories are overwritten on each helper call but safe for this single command path.
