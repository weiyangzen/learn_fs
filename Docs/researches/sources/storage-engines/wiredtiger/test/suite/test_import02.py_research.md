# sources/storage-engines/wiredtiger/test/suite/test_import02.py

Purpose: validates error handling for invalid file import operations: missing metadata, importing over an existing URI, and importing a missing file.

Important APIs and functions: `test_import02` inherits `test_import_base`. `no_metadata_helper` creates/checkpoints source data, closes the connection, opens a new home, copies the file, and attempts import using caller-provided config. Error tests use `assertRaisesWithMessage` with `wiredtiger.WiredTigerError`.

Control flow: empty `file_metadata=()` and absent `file_metadata` both call `no_metadata_helper` and expect invalid-argument failures. The existing-URI case creates a target in the destination before import and expects an error. The missing-file case collects example metadata from an existing generated table but does not copy the target file, expecting a filesystem error.

State and persistence behavior: source files are checkpointed before copy attempts. The tests exercise metadata contract validation before and during `session.create` import.

Dependencies and integration points: depends on `test_import_base.populate`, metadata cursor iteration, filesystem copy behavior, and WiredTiger import parser/validation paths.

Risks and edge cases: error-message regexes are part of the contract and can be brittle. The example metadata in the missing-file case is taken from any generated table, so it validates missing file handling rather than metadata-object identity.

Test signals: expected exceptions include invalid argument for missing metadata and `/No such file or directory/` for absent data files.
