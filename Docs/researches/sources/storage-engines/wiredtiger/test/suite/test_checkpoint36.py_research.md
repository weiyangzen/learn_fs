# sources/storage-engines/wiredtiger/test/suite/test_checkpoint36.py

Purpose: verifies API constraints for precise checkpoint when no checkpoint timestamp is available and when attempting `use_timestamp=false`.

Important APIs and types: `WiredTigerTestCase`, `wiredtiger.WiredTigerError`, `assertRaisesWithMessage`, `session.checkpoint`, and `conn.set_timestamp`.

Control flow: open with `precise_checkpoint=true`, call checkpoint before setting stable timestamp and expect an error mentioning stable timestamp; set stable timestamp 5 and checkpoint successfully; then call checkpoint with `use_timestamp=false` and expect an error.

State and persistence behavior: this is an API validation test rather than a data persistence test. It ensures precise checkpoint always has timestamp context and cannot be bypassed with `use_timestamp=false`.

Dependencies and integration points: direct checkpoint API behavior under precise checkpoint mode. Tiered hook is skipped.

Risks: the second expected error message is empty, so only the exception type is effectively checked. Comments refer to `test_checkpoint35.py`, likely a stale file-name comment.

Test signals: first and third checkpoint calls raise `WiredTigerError`; checkpoint after setting stable timestamp succeeds.
