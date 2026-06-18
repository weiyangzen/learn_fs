# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover05.py

Purpose: regression test for prepared delete artifacts that are resolved after discovery, then forced through eviction and checkpoint verification without crashing while unpacking prepared cells written by eviction.

Important APIs and types: same `test_prepare_discover04` class/name pattern in the source, `prepared_discover:`, `claim_prepared_id`, `release_evict_page`, `ignore_prepare=true`, and scenario-driven commit/rollback resolution.

Control flow: it mirrors the prepared-delete setup: baseline keys at timestamp 60, prepared removes with id 150, checkpoint, backup, reopen, discover and resolve. After resolution it opens a debug eviction session, reads keys under `ignore_prepare=true` to force page release, rolls back the eviction transaction, and runs checkpoint.

State and persistence behavior: the test focuses on disk-format and reconciliation safety. Eviction may write prepared/resolved state to disk; checkpoint verification must be able to unpack those cells after the discover/claim flow.

Dependencies and integration points: integrates prepared discovery with eviction debug hooks, reconciliation, and checkpoint disk verification. It depends on the suite subprocess backup helper.

Risks: the class and method names still say `test_prepare_discover04`, which can confuse test reporting and research indexing. The behavior is distinct from file 04 because of the forced eviction path.

Test signals: one prepared id discovered, resolution succeeds, eviction under `ignore_prepare=true` completes, and checkpoint does not crash.
