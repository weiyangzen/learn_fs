# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_debug.c

## Purpose

`lufs_debug.c` contains DEBUG-kernel support for UFS logging assertions, transaction tracing, metadata-map verification, scan-test trimming checks, and transaction statistics. The only always-compiled symbol is the global `lufs_debug` tunable because UFS ioctl code references it.

## Main Interfaces

DEBUG-only routines include `top_mataadd`, `top_matadel`, `top_mataclr`, `top_begin_debug`, `top_end_debug`, `top_delta_debug`, `top_roll_debug`, `top_init_debug`, `logmap_logscan_debug`, `logmap_logscan_commit_debug`, `logmap_logscan_add_debug`, `map_check_ldl_write`, `map_put_debug`, `map_get_debug`, `map_check_linkage`, `matamap_overlap`, `matamap_within`, `ldl_sethead_debug`, and `lufs_initialize_debug`.

## Behavior

The file maintains a circular `toptrace` buffer when `MT_TRACE` is enabled. It records transaction begin/end and delta events by device, thread, type, offset, and length.

Metadata-map helpers track legal metadata ranges and assert that deltas are within those ranges. Transaction debug state is stored in thread-specific `threadtrans_t` data keyed by `topkey`; begin/end checks verify device, transaction id, expected size, and actual recorded delta size.

Map debug routines validate hash/list/cancel-list consistency, log offset ordering across wraparound, and log-read-after-log-write correctness by rereading logged data and comparing it to the original buffer.

## Invariants And Risks

- Most checks assert `T_DONTBLOCK`, matching transaction-layer expectations.
- `matamap_within()` and `matamap_overlap()` scan per-MAPBLOCK hash ranges under map mutexes.
- Debug scan fields such as `mtm_trimrlof`, `mtm_trimclof`, and `mtm_trimalof` model safe log trimming during scan tests.
- Because this file is assertion-heavy and mostly DEBUG-only, its correctness value is in catching transaction/map corruption early rather than providing production behavior.
