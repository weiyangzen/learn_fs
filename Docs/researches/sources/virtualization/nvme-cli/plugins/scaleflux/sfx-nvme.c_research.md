# File Research: sources/virtualization/nvme-cli/plugins/scaleflux/sfx-nvme.c

ScaleFlux nvme-cli plugin implementation. It provides vendor-specific ScaleFlux commands for SMART extension logs, latency logs, bad-block data, dynamic capacity management, internal feature get/set, persistent event log dumping/parsing, namespace expansion, and a combined device status view.

Key command handlers:
- `get_additional_smart_log`: retrieves vendor log page `0xca` with `nvme_get_nsid_log`, printing normal, JSON, or raw binary output.
- `get_lat_stats_log`: retrieves read/write latency stats from log IDs `0xc1`/`0xc3`, detects Vanda version `0.0` or Myrtle `4.1`, and prints bucket histograms.
- `sfx_get_bad_block`: retrieves bad block table from `SFX_LOG_BBT`/`0xc7`, expecting exactly `256 * 4096` bytes, then prints counts and remap tables.
- `query_cap_info`: calls `nvme_query_cap`, using ioctl `SFX_GET_FREESPACE` first and falling back to admin opcode `0xd3`.
- `change_cap`: converts GB or byte capacity to 4 KiB units, sanity-checks against provisioned capacity and free RAM, prompts for shrink unless `--force`, sends admin opcode `0xd4`, and rereads partitions with `BLKRRPART`.
- `sfx_set_feature` / `sfx_get_feature`: use vendor admin opcodes `0xd5`/`0xd6`; feature IDs include atomic writes, update provision capacity, and clean card.
- `sfx_dump_evtlog`: dumps NVMe persistent event log, optionally parses ScaleFlux-specific event records into a text file.
- `sfx_expand_cap`: expands the last namespace with `nvme_admin_ns_mgmt` cdw10 `0x0e` and a packed ScaleFlux payload.
- `sfx_status`: aggregates sysfs PCIe data, identify controller, SMART, ScaleFlux extended health, additional SMART, capacity/freespace, and atomic feature state into human or JSON output.

Important internal flows:
- `nvme_query_cap` uses a Linux ioctl path when available, otherwise uses vendor passthrough. This makes behavior dependent on both kernel driver support and controller firmware support.
- Capacity conversion uses IDEMA formulas and assumes sector/LBA relationships in `IDEMA_CAP`, `IDEMA_CAP2GB`, and `IDEMA_CAP2GB_LDS`.
- `change_sanity_check` enforces target capacity between 1x and 4x provisioned capacity and estimates memory needed for capacity expansion.
- `sfx_clean_card` validates the handle is a character controller device before issuing `NVME_IOCTL_CLR_CARD`.

Notable edge cases:
- `sfx_dump_evtlog` returns `0` from the CLI handler even after assigning `err`, so caller-visible failure propagation is incomplete.
- Event parsing indexes `sfx_evtlog_warning[code_type]` and `sfx_evtlog_error[code_type]` without explicit bounds checks after decoding firmware event codes.
- `sfx_status` depends heavily on Linux sysfs paths under `/sys/class/nvme/<ctrl>/device/*`; missing AER/link files cause hard failure.
- Namespace derivation in `sfx_expand_cap` falls back to the last character of the device name for namespace ID when invoked on a namespace handle, which is fragile for multi-digit namespace IDs.

External dependencies:
- libnvme admin passthrough/get-log helpers.
- nvme-cli shared parsing/output helpers.
- Linux ioctls `BLKRRPART`, `SFX_GET_FREESPACE`, and `NVME_IOCTL_CLR_CARD`.
- sysfs PCIe/NVMe attributes for `sfx_status`.
