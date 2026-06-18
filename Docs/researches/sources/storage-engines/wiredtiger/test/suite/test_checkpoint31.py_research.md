# sources/storage-engines/wiredtiger/test/suite/test_checkpoint31.py

Purpose: verifies named checkpoint cursors can be opened and read from a read-only connection, particularly when prepared transaction durable timestamps mean later values should not be visible in the named checkpoint.

Important APIs and types: prepared transactions, named `session.checkpoint("name=ckpt1")`, `reopen_conn(config="readonly=true")`, and checkpoint cursor lookup.

Control flow: create two prepared updates to key `2`; checkpoint `ckpt1` with stable timestamp between commit and durable timestamp of the second update; take a later unnamed checkpoint at stable 40; reopen normally and read `ckpt1`; reopen read-only and read `ckpt1` again.

State and persistence behavior: the named checkpoint must persist its visibility state after restart and be readable without write access. Expected value for key `2` is the first transaction's value.

Dependencies and integration points: checkpoint cursor opening in read-only mode, prepared transaction timestamp handling, and named checkpoint metadata. Skipped for disaggregated hooks.

Risks: no tiered skip is present; behavior may be environment-sensitive if named checkpoint support changes. Error paths are not exercised here.

Test signals: both normal and read-only reopened connections find key `2` in `ckpt1` and return value `20`.
