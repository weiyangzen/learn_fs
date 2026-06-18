# sources/storage-engines/wiredtiger/test/suite/test_debug_mode06.py

Purpose: validates `debug_mode=(slow_checkpoint=true)` by making checkpoints deliberately slow and confirming the mode can be disabled.

Important APIs and control flow: `insert_data(assert_time=0)` creates a file, writes one key, calls `session.checkpoint()`, and optionally reads `wiredtiger.stat.conn.checkpoint_time_recent` from `statistics:` to assert the recent checkpoint time is at least a minimum. `test_slow_checkpoints` expects at least 10 ms; `test_slow_checkpoints_off` reconfigures `debug_mode=(slow_checkpoint=false)` and reruns without the timing assertion.

State and persistence: the file is checkpointed, but the key signal is checkpoint latency induced by debug mode.

Dependencies and integration: uses `wttest`, `wiredtiger`, session create/open cursor/checkpoint, and `conn.reconfigure`.

Risks and test signals: timing tests can be environment-sensitive. The value is that it catches loss of slow-checkpoint debug plumbing and validates the reconfigure path for turning it off.
