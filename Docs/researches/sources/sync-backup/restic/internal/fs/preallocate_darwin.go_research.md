# sources/sync-backup/restic/internal/fs/preallocate_darwin.go

Purpose: Darwin file preallocation using `F_PREALLOCATE`.

Important APIs: `PreallocateFile`.

Control flow and state: Tries contiguous allocation with `F_ALLOCATECONTIG|F_ALLOCATEALL`; if that fails, retries non-contiguous `F_ALLOCATEALL`.

Dependencies and integration: Used where restic wants to reserve output file space before writing.

Risks: Preallocation can fail depending on filesystem free-space layout or unsupported filesystems. The function returns the second allocation error if both attempts fail.

Test signals: `preallocate_test.go` validates behavior for zero, small, page, and MiB sizes, skipping unsupported filesystems.
