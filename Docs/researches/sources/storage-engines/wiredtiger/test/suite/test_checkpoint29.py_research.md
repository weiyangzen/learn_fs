# sources/storage-engines/wiredtiger/test/suite/test_checkpoint29.py

Purpose: tests checkpoint cursor behavior after bulk cursor activity creates a single-file checkpoint that is not valid as the system checkpoint.

Important APIs and types: `session.open_cursor(..., "bulk")`, `session.checkpoint`, internal checkpoint name `WiredTigerCheckpoint`, `expectedStdoutPattern`, and `wiredtiger.WiredTigerError`.

Control flow: create an empty table, take a system checkpoint, open and close a bulk cursor, attempt to open `checkpoint=WiredTigerCheckpoint` and expect failure plus warning, take another system-wide checkpoint, then open the checkpoint cursor successfully.

State and persistence behavior: bulk cursor close creates per-file checkpoint metadata that can be inconsistent with the system checkpoint. A subsequent database-wide checkpoint repairs the metadata state.

Dependencies and integration points: exercises bulk-load metadata interaction with checkpoint cursor opening. Skipped for tiered and disaggregated hooks.

Risks: warning text is part of the test contract. Precise checkpoint mode requires a stable timestamp seed.

Test signals: first checkpoint cursor open raises with stdout containing `could not open the checkpoint`; second open after full checkpoint succeeds.
