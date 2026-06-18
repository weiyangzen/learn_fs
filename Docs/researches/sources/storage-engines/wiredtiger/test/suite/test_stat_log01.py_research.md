<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat_log01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat_log01.py

Purpose: tests statistics log file creation under default path, custom path, periodic and on-close modes, plus readonly reopen compatibility after statistics logging is recorded in base config.

Important APIs/types/functions: `test_stat_log01` manually opens connections with `wiredtiger_open`, disables default setup/session hooks, uses `glob` to find `WiredTigerStat.[0-9]*`, sleeps for periodic logging, and closes connections to trigger on-close logging. `test_stat_log01_readonly` uses normal fixture setup and then `wiredtiger_open(..., "readonly")`.

Control flow: each logging test opens a connection with `statistics=(fast)` and a `statistics_log` config, waits or closes as needed, and asserts at least one stats file exists in the expected directory. The readonly test closes a logged home and verifies a readonly open succeeds.

State and persistence behavior: stats logging writes external `WiredTigerStat` files and may persist logging config into base configuration. Readonly open validates those persisted settings do not require writes.

Dependencies/integration points: covers stats logging, filesystem paths, on-close behavior, readonly open, and tiered skip for readonly crash. Risks include sleep timing and file glob assumptions; signals are stats file presence and successful readonly open.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat_log01.py -->
