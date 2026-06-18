<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/sweep_util.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/sweep_util.py

Purpose: Small base class for tests that must wait for WiredTiger data-handle sweep activity without spinning until the global task timeout.

Important APIs and types: `sweep_util` extends `wttest.WiredTigerTestCase` and provides `wait_for_sweep(baseline=None, increment=1, statistic=stat.conn.dh_sweeps, session=None, timeout=60, poll_interval=0.5)`.

Control flow: The method samples the chosen statistics cursor value when no baseline is supplied, then repeatedly opens `statistics:`, reads the statistic tuple value, and returns once the value has advanced by `increment`. Between polls it asserts the timeout has not elapsed and sleeps for the configured interval.

State and persistence behavior: It does not mutate data directly; it observes connection statistics maintained by WiredTiger. Each poll opens and closes a statistics cursor through `wttest.open_cursor`, so cursor lifetime is bounded even on assertion failures.

Dependencies and integration points: Depends on `wiredtiger.stat`, suite cursor context manager `wttest.open_cursor`, and the caller's session. Tests can override the statistic to wait for other sweep-related counters.

Risks: Timing remains environment-sensitive because sweep is asynchronous. Too-small timeouts can fail slow machines, while too-large intervals delay failure. If the connection has statistics disabled, the helper cannot observe the expected signal.

Test signals: The returned observed counter value and timeout assertion message show whether the sweep server advanced enough within the expected window.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/sweep_util.py -->
