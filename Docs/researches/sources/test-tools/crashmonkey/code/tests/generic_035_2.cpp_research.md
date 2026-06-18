# sources/test-tools/crashmonkey/code/tests/generic_035_2.cpp

Purpose: directory rename variant of xfstests generic/035. It renames one child directory over another and fsyncs the destination directory to catch stale directory-entry replay issues.

Important APIs/types/functions: source class is named `Generic321_2`; it uses `mkdir`, `open(..., O_DIRECTORY)`, `rename`, `fstat`, `fsync`, `Checkpoint`, `rmdir`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: `setup()` creates a parent plus two child directories and syncs. `run()` opens the destination directory, renames the first child to the destination path, checks the open fd with `fstat`, reopens/fsyncs the destination directory, and checkpoints. `check_test()` removes the destination and then the parent.

State/persistence behavior: after replay, there should be exactly one child directory and no stale references that keep the parent non-empty after cleanup.

Dependencies/integration: raw Linux directory rename and fsync semantics.

Risks/test signals: overwriting directories is filesystem-sensitive and can fail if directories are not empty. The check focuses on `rmdir` cleanup rather than enumerating all names.
