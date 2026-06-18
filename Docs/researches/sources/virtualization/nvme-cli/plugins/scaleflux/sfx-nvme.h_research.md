# File Research: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-nvme.h

ScaleFlux plugin command registration header. It defines `CMD_INC_FILE` as `plugins/scaleflux/sfx-nvme`, includes `cmd.h`, and registers the `sfx` plugin with description `ScaleFlux vendor specific extensions`.

Registered commands:
- `smart-log-add` -> `get_additional_smart_log`
- `lat-stats` -> `get_lat_stats_log`
- `get-bad-block` -> `sfx_get_bad_block`
- `query-cap` -> `query_cap_info`
- `change-cap` -> `change_cap`
- `set-feature` -> `sfx_set_feature`
- `get-feature` -> `sfx_get_feature`
- `dump-evtlog` -> `sfx_dump_evtlog`
- `expand-cap` -> `sfx_expand_cap`
- `status` -> `sfx_status`

This header is consumed by nvme-cli’s command-generation mechanism via `CREATE_CMD` in the `.c` file and final `define_cmd.h`.
