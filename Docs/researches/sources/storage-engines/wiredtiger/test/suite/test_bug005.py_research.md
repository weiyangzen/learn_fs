# sources/storage-engines/wiredtiger/test/suite/test_bug005.py

Purpose: regression test that `verify` succeeds when a file has additional trailing bytes after the last checkpoint. It targets file-level btree verification.

Important APIs are `session.create`, cursor inserts, `verifyUntilSuccess`, `reopen_conn`, and direct filesystem append. Control flow creates `file:test_bug005`, writes 999 string key/value pairs, verifies in-memory state, reopens to force data to disk, verifies again, appends literal random data to the underlying file, and verifies once more. State behavior is persistent file contents, including tolerated bytes after the checkpointed extent. Dependencies are `simple_key/simple_value` and harness retry helpers. Risks include opening `test_bug005` directly assumes the file URI maps to that relative filename, and append mode may behave differently across platforms. Test signal is successful verification after direct trailing-data mutation.
