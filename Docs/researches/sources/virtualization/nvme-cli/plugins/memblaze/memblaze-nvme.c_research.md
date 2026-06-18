# File Research: sources/virtualization/nvme-cli/plugins/memblaze/memblaze-nvme.c

This file implements the Memblaze nvme-cli plugin. It contains legacy Memblaze commands and newer `-x` commands for updated SMART, latency, high-latency, and performance logs.

Major command groups:
- Legacy SMART:
  - `mb_get_additional_smart_log()` reads log page `0xca` and chooses old Memblaze or newer Intel-like formatting based on controller model name.
- Power management:
  - `mb_get_powermanager_status()` gets feature `0x02`.
  - `mb_set_powermanager_status()` sets feature `0x02`.
- Legacy high latency:
  - `mb_set_high_latency_log()` sets feature `0xe1`.
  - `mb_high_latency_log_print()` reads log page `0xc3` repeatedly and writes `log_c3.csv`.
- Firmware:
  - `mb_selective_download()` downloads firmware chunks and commits with select values for `OOB`, `EEP`, or `ALL`.
- Legacy latency statistics:
  - `mb_set_lat_stats()` gets/sets latency tracking feature `0xe2`.
  - `mb_lat_stats_log_print()` reads log pages `0xc1`/`0xc2` and writes `log_c1.csv` or `log_c2.csv`.
- Error clearing:
  - `memblaze_clear_error_log()` sets feature `0xf7` with value `0x534d0001`.
- Newer `-x` logs/features:
  - `mb_get_smart_log_add()` reads `LID_SMART_LOG_ADD` (`0xca`) and prints versioned layouts.
  - `mb_set_latency_feature()` sets `FID_LATENCY_FEATURE` (`0xd0`) with monitor bits, command mask, and thresholds.
  - `mb_get_latency_feature()` reads and decodes feature `0xd0`.
  - `mb_get_latency_stats()` reads `LID_LATENCY_STATISTICS` (`0xd0`).
  - `mb_get_high_latency_log()` reads `LID_HIGH_LATENCY_LOG` (`0xd1`).
  - `mb_get_performance_stats()` reads `LID_PERFORMANCE_STATISTICS` (`0xd2`).

Key internal structures:
- Legacy/new SMART helpers rely on `nvme_memblaze_smart_log` and `nvme_p4_smart_log` from `memblaze-utils.h`.
- New SMART layout `smart_log_add` supports versions 0, 2, and 3 with different item structures and attribute maps.
- `latency_stats` supports version 2.0 with read/write/trim bucket arrays.
- `high_latency_log` supports version 1 with 1024 detailed latency entries.
- `performance_stats` supports versions 1 and 2 with up to 24 hourly timestamp groups and 3600 entries per timestamp.

Important implementation details:
- `getlogpage_format_type()` treats newer models as Intel-format and older `P...` models before `P5920` as Memblaze-format.
- Legacy high-latency parsing stops on `deadbeef`, zero latency/revision, or command error.
- Firmware download validates 4-byte image alignment, allocates a full firmware buffer, transfers in 4 KiB chunks, then commits with a vendor-specific select code.
- Newer performance stats handle odd duration by requesting one extra timestamp to avoid non-dword-alignment issues, while dumping only the requested logical size.
- Temperature fields are often printed in both Celsius and Kelvin through `K2C()`.

Notable quirks:
- Several legacy print paths allocate tiny buffers for normalized/raw values where stack arrays would be simpler.
- Some raw casts such as `*(__u16 *)raw` assume unaligned access is safe.
- `mb_get_performance_stats()` calls `exit(1)` on invalid duration, which is abrupt for a plugin command path.
- The file mixes older CSV-producing commands with newer stdout/raw commands, so behavior differs significantly between legacy and `-x` interfaces.
