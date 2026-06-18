# sources/storage-engines/wiredtiger/test/suite/test_layered_config06.py

Purpose: validates rollback-to-stable behavior in a disaggregated PALite setup: recovery RTS after crash should not roll back disaggregated storage, while explicit runtime RTS still should.

Important APIs/types/functions: uses `SimpleDataSet`, `simulate_crash_restart`, custom `conn_extensions` loading `page_log/palite`, manual `early_setup` creating shared `kv_home` symlink for follower, `skip_for_hook("tiered")`, and `rollback_to_stable`.

Control flow: it creates and populates a normal table under disaggregated PALite config, updates three keys at commit timestamp 30, sets stable timestamp 20, checkpoints, and simulates crash/restart. After restart, it verifies recovery did not roll back the timestamp-30 updates. It then calls runtime `rollback_to_stable` and verifies the same keys return to original dataset values.

State and persistence behavior: distinguishes crash recovery state from runtime rollback state. Disaggregated storage should keep post-stable writes after crash recovery in this context, but runtime RTS remains functional.

Dependencies/integration points: PALite page log extension, crash restart helper, timestamped updates, WiredTiger recovery, and rollback-to-stable.

Risks: no `disagg_test_class` decorator; setup is manual and platform-sensitive around symlinks. It skips tiered hook and handles Windows extension availability.

Test signals: pass means recovery RTS is disabled/benign for disaggregated context while explicit RTS still rewinds unstable updates.
