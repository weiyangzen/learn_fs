# sources/sync-backup/git-lfs/tools/util_windows_test.go

Purpose: Windows-specific block clone tests.

Important APIs/types/functions: `TestCloneFile` and helper `fillFile`.

Control flow: chooses `REFS_TEST_DIR` or current working directory, skips if clone support probe fails, then writes deterministic content at several sizes, clones, hashes destination, and compares hashes.

State and persistence: creates temp files in the selected test directory and writes/truncates content.

Dependencies and integration points: validates Windows optimization used by `CopyWithCallback`.

Risks: requires ReFS/block-clone-capable filesystem to run; temp files are not explicitly removed in the shown test body.

Test signals: strong size-boundary coverage when environment supports the feature.
