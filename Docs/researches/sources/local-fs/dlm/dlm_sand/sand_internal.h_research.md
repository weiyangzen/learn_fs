# File Research: sources/local-fs/dlm/dlm_sand/sand_internal.h

## Purpose
Central internal header for `dlm_sand`, defining daemon globals, configuration options, on-disk layout constants, cluster state structures, and cross-file function prototypes.

## Key Definitions
- Configuration paths: `/etc/dlm/dlm.conf`, `/run/dlm_sand.pid`, `/var/log/dlm_sand.log`.
- Option indexes for daemon/debug/fencing/protocol/port/mark/local node and IP settings.
- Event LV layout: 512 MiB total, fixed offsets for config, nodes, summary, records, and lock-manager data.
- Maximum node model: 2000 active node ids with 2048-sized aligned arrays and 256-byte nodeid bitmaps.
- On-disk structures: `dlm_events_header`, `dlm_events_summary`, `dlm_events_node`, `log_record`.
- Runtime structures: `current_event`, `vg_lockspace`, `vg_node`, `dlm_node`, `rd_sanlock`, `lockspace`.

## Interfaces Declared
- Kernel/configfs actions from `action.c`.
- Config loading and online setting from `config.c`.
- Main-loop helpers from `main.c`.
- Logging functions from `log.c`.

## Notable Design
- Uses the `EXTERN` macro pattern so `main.c` can define globals and other C files can declare them.
- Separates VG-level sanlock host tracking from DLM lockspace-level event processing.
- Stores per-lockspace recovery state in fixed arrays indexed by `nodeid - 1`.

## Risks / Gaps
- Fixed-size arrays for 2000 nodes are simple but large; each `lockspace` carries multiple 2048-byte and 2000-entry generation arrays.
- `struct log_record` relies on exact layout comments and CRC length assumptions; future field changes require careful compatibility work.
- Includes many system and project headers globally, increasing coupling across the `dlm_sand` implementation.
