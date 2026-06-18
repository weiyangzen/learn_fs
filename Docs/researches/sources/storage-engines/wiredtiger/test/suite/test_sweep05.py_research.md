<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep05.py

Purpose: extra-long tests for detecting sessions that have not run session sweep recently, with separate coverage for five-minute and sixty-minute violation counters.

Important APIs/types/functions: `test_sweep05` uses `wttest.extralongtest`, `wiredtiger.stat.conn.no_session_sweep_5min`, `no_session_sweep_60min`, verbose sweep filtering, `time.sleep`, session `reset`, and helper methods `get_stats`, `assert_stats`, `create_table`, and `use_session`.

Control flow: `test_short` creates two tables and two extra sessions, repeatedly uses/resets one session while leaving others idle, sleeps enough to trigger five-minute detections, verifies counters, resets idle sessions, then repeats to confirm counters increment cumulatively. `test_long` keeps sessions swept for 55 minutes, then allows selected sessions to become idle long enough to trigger 5-minute and 60-minute counters.

State and persistence behavior: state is runtime session sweep timestamps and cumulative connection counters, not persisted table data. Table reads create session handle activity; `session.reset` marks sweep progress.

Dependencies/integration points: covers session sweep monitoring, verbose warning output, connection stats, and long wall-clock behavior. Risks are extreme runtime and timing sensitivity; signals are exact cumulative counter values after sleeps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep05.py -->
