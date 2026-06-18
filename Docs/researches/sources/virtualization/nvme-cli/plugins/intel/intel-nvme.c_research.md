# File Research: sources/virtualization/nvme-cli/plugins/intel/intel-nvme.c

This file implements Intel nvme-cli plugin commands for identify-controller vendor fields, SMART/temperature/marketing logs, latency statistics, internal firmware logs, and latency feature controls.

Command families:
- `id_ctrl()`: delegates to nvme-cli’s `__id_ctrl()` with Intel vendor-specific field decoding.
- `get_additional_smart_log()`: reads Intel additional SMART log page `0xca`.
- `get_market_log()`: reads marketing-name log page `0xdd`.
- `get_temp_stats_log()`: reads temperature statistics log page `0xc5`.
- `get_lat_stats_log()`: reads read/write latency statistics log pages `0xc1`/`0xc2`.
- `get_internal_log()`: exports Intel internal firmware logs via vendor opcode `0xd2`.
- `enable_lat_stats_tracking()`: gets/sets feature `0xe2`.
- `set_lat_stats_thresholds()`: sets Optane latency bucket thresholds via feature `0xf7`.

Important structures:
- `nvme_additional_smart_log_item` and `nvme_additional_smart_log`: Intel additional SMART attributes with normalized and 48-bit raw values.
- `nvme_vu_id_ctrl_field`: Intel identify-controller vendor-specific area fields such as subsystem status, health, bootloader, world-wide identifier, and MIC versions.
- `intel_temp_stats`: temperature statistics fields.
- `intel_lat_stats` and `optane_lat_stats`: NAND and Optane latency-stat layouts.
- Internal log structures: `intel_vu_log`, `intel_vu_nlog`, `intel_assert_dump`, `intel_event_dump`, `intel_event_header`, and command selector `intel_cd_log`.

Output support:
- Additional SMART supports normal, raw binary, and JSON output.
- Latency statistics support normal, raw binary, and JSON output.
- Identify-controller vendor fields support normal output and JSON through the root object passed by `__id_ctrl()`.

Latency-statistics logic:
- Reads the longest latency log first because Optane clears stats when the latency log is pulled.
- Interprets media version from the first four bytes.
- Supports NAND major revisions 3 and 4 with linear or logarithmic bucket ranges.
- Supports Optane major version 1000 minor 0 by querying bucket thresholds from feature `0xf7`.
- Uses helper formatting for microseconds/milliseconds/seconds and infinity bucket bounds.

Internal firmware log logic:
- Builds default output filenames from log type and controller serial number: `Nlog_<sn>.bin`, `EventLog_<sn>.bin`, or `AssertLog_<sn>.bin`.
- Reads a header with opcode `0xd2`, then handles old firmware formats separately.
- Supports log type 0 nlog, 1 event log, and 2 assert log.
- Can select all cores/nlogs or specific region/nlog.
- Writes binary log content to the output file and optionally prints verbose nlog metadata.

Notable quirks:
- `OPTANE_V1000_BUCKET_LEN` is defined twice with the same value.
- JSON support for Intel latency revision 4 handles minor versions 0-5, while text output accepts 0-6.
- Several internal log sizes and offsets are handled in dwords, while `data_len` is bytes; the code is careful in places but the mixture makes this command sensitive to off-by-four errors.
