<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config07.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config07.py

Purpose: tests documented log file preallocation/extend sizing through the `file_extend` configuration.

Important APIs and control flow: scenarios vary `file_extend=(log=...)` across defaults, disabled preallocation, valid sizes, invalid too-small/too-large values, sizes above log file max, and mixed data/log extend config. The test closes the default connection, opens with logging and `file_max=1M`, rejects invalid extend sizes, otherwise populates 5000 records, checkpoints, and polls for a `*Prep*` preallocation file with the expected size.

State, persistence, and dependencies: persistent artifacts are log files and preallocated prep files in the home. Dependencies are `fnmatch`, `os.stat`, time polling, log manager preallocation, and WiredTiger checkpoint/log write paths.

Integration points: covers connection config parsing, logging, file extension/preallocation, and checkpoint-induced log activity.

Risks and test signals: timing-sensitive polling can fail on very slow systems, and filesystem allocation behavior may vary. The strongest signal is exact prep file size or correct invalid-config error.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config07.py -->
