# sources/sync-backup/restic/internal/fs/preallocate_test.go

Purpose: Cross-platform test for `PreallocateFile`.

Important APIs: `TestPreallocate`.

Control flow and state: Iterates sizes `0`, `1`, `4096`, and `1 MiB`, opens a temp file, calls `PreallocateFile`, skips `ENOTSUP`, then asserts size equals requested size or allocated block count is positive.

Dependencies and integration: Exercises platform implementations through a single contract.

Risks: Assertion allows either exact size or allocated blocks, which accommodates platform differences but is not strict about sparse allocation.

Test signals: Confirms preallocation functions do not fail unexpectedly on supported filesystems.
