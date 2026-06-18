# sources/storage-engines/wiredtiger/test/suite/test_import05.py

Purpose: verifies file import rejects objects whose aggregated durable timestamps are newer than the selected global timestamp, for both metadata import and repair import.

Important APIs and functions: scenarios cover latest operation type (`insert` or `delete`), import mode (`repair=false` with `file_metadata` or `repair=true`), and comparison timestamp (`oldest` or `stable`). The test uses `expectedStderrPattern` and `assertRaisesException`.

Control flow: it writes all but the last record, checkpoints, then either inserts the last record or deletes the first record at the last timestamp and checkpoints again. After copying the file to a new home, it constructs import config with optional `compare_timestamp=stable_timestamp`. It first imports with global timestamp unset and expects failure, then sets the chosen global timestamp to one less than the last operation and expects start or stop timestamp failure, then sets it equal to the last timestamp and expects success.

State and persistence behavior: the object's aggregated newest start/stop durable timestamps are persisted in metadata/checkpoint state and compared against oldest or stable timestamp during import.

Dependencies and integration points: depends on import timestamp validation, repair mode metadata reconstruction, durable timestamp aggregation, and error reporting.

Risks and edge cases: exact stderr patterns are part of the test. Delete mode specifically validates stop timestamp handling, which can regress separately from start timestamp handling.

Test signals: failures mention `newest start durable` or `newest stop durable` as appropriate; final import succeeds after advancing the selected global timestamp.
