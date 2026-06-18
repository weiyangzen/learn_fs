# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable36.py

Purpose: tests rollback of a checkpointed fast truncate where stable data must be restored. It runs runtime and recovery modes, column/integer row formats, and worker counts.

Important APIs/types/functions: direct `wttest.WiredTigerTestCase` subclass with `verify_rts_logs`. Defines `truncate` supporting real truncate and a disabled remove-loop mode, plus `check`. Uses `session.truncate`, `simulate_crash_restart`, `conn.rollback_to_stable`, `stat.dsrc.rec_page_delete_fast`, and `stat.conn.rec_page_delete_fast_instantiated`.

Control flow: writes baseline data at timestamp 10, sets stable to 10, reopens to clear memory, truncates most keys at timestamp 20, verifies fast-delete occurred, checkpoints, then either restarts or calls runtime RTS. It then checks page-instantiation stats and verifies all rows are visible at timestamps 15 and 25.

State and persistence behavior: unstable fast-delete pages must be instantiated or otherwise restored so stable content is visible. Recovery and runtime paths should both restore table contents.

Dependencies and integration points: integrates fast-delete reconciliation, checkpoint, restart simulation, and RTS page instantiation accounting.

Risks: fast-delete depends on page layout; the remove-loop scenario is commented out, indicating only true truncate currently matters. TSan or slow environments could affect timing less than in checkpoint-race tests.

Test signals: positive fast-delete pages, positive read-deleted/page-instantiated stats for truncate mode, and full row-count/value checks after rollback.
