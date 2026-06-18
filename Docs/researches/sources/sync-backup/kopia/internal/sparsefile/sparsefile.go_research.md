<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/sparsefile/sparsefile.go -->
# sources/sync-backup/kopia/internal/sparsefile/sparsefile.go

- Purpose: Copies data to a seekable destination while converting all-zero blocks into sparse file holes.
- Important APIs/types/functions: `Copy`, `copyBuffer`, `isAllZero`.
- Control flow: `Copy` borrows a shared buffer from `iocopy`, slices it to requested size, and delegates. `copyBuffer` reads into the buffer, seeks over zero blocks, writes non-zero blocks, accounts bytes, and handles read/write/short-write errors.
- State and persistence: Persistent effects are writes/seeks on the destination file; no package state beyond borrowed buffer lifecycle.
- Dependencies and integration points: Integrates `io`, `pkg/errors`, and `internal/iocopy`.
- Risks and edge cases: `isAllZero` is called on the full buffer rather than `buf[:nr]`, so short reads with stale non-zero bytes could defeat sparse skipping.
- Test signals: `sparsefile_test.go` checks content equivalence for empty, hole, mixed, and null sparse copies on non-Windows systems.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/sparsefile/sparsefile.go -->
