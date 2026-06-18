# sources/storage-engines/wiredtiger/test/suite/test_reconfig01.py

Purpose: smoke-tests runtime `WT_CONNECTION::reconfigure` for shared cache, eviction, statistics, capacity, checkpoints, statistics logging, and file manager settings.

Important APIs and types: `self.conn.reconfigure`, `wiredtiger.WiredTigerError`, `assertRaisesWithMessage`, and configuration strings for `shared_cache`, `eviction`, `io_capacity`, `checkpoint`, `statistics_log`, and `file_manager`.

Control flow: each test method applies a sequence of legal reconfiguration strings and expects success. Negative cases assert too-low `io_capacity` reports `/below minimum/` and non-reconfigurable log path reports `/unknown configuration key/`.

State and persistence behavior: no table state is required; it validates live connection configuration mutation. Some changes affect background components such as eviction and statistics logging.

Dependencies and integration points: connection configuration parser, runtime reconfigurability flags, eviction server, statistics logger, and file manager.

Risks: broad smoke tests can miss semantic effects beyond successful parsing. They are still valuable for guarding config keys and reconfigurability contracts.

Test signals: successful reconfigure calls do not raise; invalid values raise expected errors.
