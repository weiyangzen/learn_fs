# sources/storage-engines/wiredtiger/test/suite/test_reconfig02.py

Purpose: tests runtime logging-related reconfiguration, especially toggling log removal/preallocation/zero-fill and rejecting immutable log settings.

Important APIs and types: custom `setUpConnectionOpen`, `self.conn.reconfigure`, `fnmatch.filter`, `os.listdir`, `time.sleep`, `reopen_conn`, and log configuration keys.

Control flow: simple reconfig toggles `remove`, `prealloc`, and `zero_fill`. Negative tests assert `enabled`, `compressor`, `file_max`, `path`, and `recover` cannot be reconfigured. The prealloc test waits for `*Prep*` files after enabling preallocation. The remove test writes data, reopens to roll logs, enables log removal, checkpoints, waits, and confirms original log files are gone.

State and persistence behavior: creates a logged table and log files; reconfiguration affects log preallocation and cleanup behavior on disk.

Dependencies and integration points: logging subsystem, background preallocation/removal threads, checkpoint, filesystem listing, and connection reopen.

Risks: sleep-based background-thread tests can be timing-sensitive on slow systems, though loops are used for preallocation.

Test signals: expected log files appear/disappear after reconfiguration, and immutable log settings raise `/unknown configuration key/`.
