<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep03.py

Purpose: verifies `close_idle_time=0` disables idle handle sweeping while still allowing explicit drop cleanup paths to close handles and reclaim cache.

Important APIs/types/functions: `test_sweep03` extends `sweep_util` and `suite_subprocess`; it uses `wait_for_sweep`, `stat.conn.dh_sweep_dead_close`, `cache_bytes_inuse`, `dh_sweeps`, `dropUntilSuccess`, and verbose sweep filtering. Scenarios cover row and VLCS table formats.

Control flow: `test_disable_idle_timeout1` creates 40 tables, waits for two sweeps, and asserts no dead handles were closed. Drop-force and drop tests create a table, fill it, capture cache/close stats, drop with or without `force=true`, wait for sweeps, and compare cache and close counts.

State and persistence behavior: idle handles remain open when idle timeout is disabled. Dropped objects should release cache and handles through drop-specific paths rather than normal idle sweep; disaggregated row mode may close two handles for force drop.

Dependencies/integration points: covers file-manager idle timeout, sweep server stats, forced and normal drop, cache reclamation, and hook-specific expectations. Risks include timing and hook exclusions; signals are zero idle closes, expected close counts for force drop, and reduced cache use after drop.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep03.py -->
