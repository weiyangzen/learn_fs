<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate20.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate20.py

Purpose: exercises `debug_mode.disagg_slow_truncate_follower` parsing and verifies the knob selects slow versus fast follower truncate behavior.

Important APIs/types/functions: uses `LayeredFastTruncateConfigMixin`, `wiredtiger.WiredTigerError`, `wiredtiger.stat`, `stat.conn.layered_curs_remove`, `reopen_conn`, `reconfigure`, `reopen_disagg_conn`, and `expectedStderrPattern`.

Control flow: the config smoke tests open connections with the knob true, false, omitted, toggle it by reconfigure, and reject a non-boolean value. Behavior tests populate 500 leader keys, reopen as follower with the knob set, capture `layered_curs_remove`, truncate 100-400, and compare stat deltas. Slow mode must call cursor remove once per key; fast mode must not call cursor remove when ingest is empty.

State and persistence behavior: the knob affects the follower truncate implementation path, not the logical output. The observed state is a connection statistic showing whether per-key remove was used.

Dependencies/integration points: integrates connection config parsing, debug-mode reconfiguration, fast truncate, and statistics. Risks include stat renames or slow path behavior changing. Test signals are accepted/rejected config and exact/remove-zero stat deltas.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate20.py -->
