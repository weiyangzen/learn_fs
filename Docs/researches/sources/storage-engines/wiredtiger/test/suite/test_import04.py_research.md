# sources/storage-engines/wiredtiger/test/suite/test_import04.py

Purpose: covers success and failure scenarios for table import, including existing target objects, dropped objects with retained files, missing files, missing table config, and missing file metadata. It is skipped for tiered storage.

Important APIs and functions: `test_import04` inherits `test_import_base`, uses `make_scenarios` for simple and named-column tables, and relies on `wiredtiger.WiredTigerError` plus `assertRaisesException`/`assertRaisesWithMessage`.

Control flow: it creates and checkpoints a target table, exports table and file metadata, reopens the same home and confirms importing over an existing table fails, drops the table with `remove_files=false` and successfully imports it, then creates a fresh `IMPORT_DB`. In the new home it first expects failure before the file is copied, then expects invalid-argument failures when omitting table config or file metadata, then performs a valid import, verifies data/metadata, appends rows, and checkpoints.

State and persistence behavior: drop-without-remove leaves the backing file as importable state. Timestamp advancement is required before importing timestamped data. Metadata completeness is enforced for non-repair table import.

Dependencies and integration points: integrates drop semantics, metadata cursor export, import parser validation, file existence checks, and table verification.

Risks and edge cases: the test relies on single-file table backing names and is not valid for tiered hooks. Error-message matching may need updates if WiredTiger changes diagnostic text.

Test signals: expected failures occur in invalid states; valid imports retain values and metadata; post-import updates work.
