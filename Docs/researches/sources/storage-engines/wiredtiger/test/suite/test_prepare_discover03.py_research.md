# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover03.py

Purpose: ensures `prepared_discover:` reports an error if it is closed while another persisted prepared transaction remains unclaimed, and that an already claimed prepared id cannot be claimed again.

Important APIs and types: `prepared_discover:`, `claim_prepared_id`, `assertRaisesWithMessage`, `wiredtiger.WiredTigerError`, backup/reopen helpers, and two separate prepared transactions with ids 123 and 150.

Control flow: it creates committed baseline data, then prepares one insert transaction with id 123 and another update transaction with id 150. After stable advancement, checkpoint, backup, and reopen, it walks the discover cursor, claims and commits only the first prepared id, breaks the loop, tries to claim id 123 again, and finally closes the discover cursor expecting an error about one unclaimed prepared transaction.

State and persistence behavior: persisted prepare metadata must track both unclaimed and claimed states. Closing the discover cursor is part of the correctness contract because unresolved prepared artifacts must not be ignored.

Dependencies and integration points: exercises recovery, backup, prepared metadata accounting, duplicate-claim rejection, and discover cursor close validation.

Risks: the loop asserts discovered id 123, so ordering matters; if discovery order changes, this test may become brittle unless the implementation preserves deterministic id order.

Test signals: duplicate claim raises `WiredTigerError`, and closing the cursor raises a message matching `Found 1 unclaimed prepared transactions`.
