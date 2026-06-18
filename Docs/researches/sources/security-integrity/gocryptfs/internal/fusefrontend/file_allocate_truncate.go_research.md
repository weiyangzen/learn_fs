<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_allocate_truncate.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/file_allocate_truncate.go

- Purpose: Implements FUSE fallocate and truncate over encrypted block geometry, including header creation, size translation, hole allocation, and partial-block preservation.
- Important APIs/types/functions: `const FALLOC_DEFAULT = 0x00`, `const FALLOC_FL_KEEP_SIZE = 0x01`, `var allocateWarnOnce sync.Once`, `func (f *File) Allocate(ctx context.Context, off uint64, sz uint64, mode uint32) syscall.Errno`, `func (f *File) truncate(newSize uint64) (errno syscall.Errno)`, `func (f *File) statPlainSize() (uint64, error)`, `func (f *File) truncateGrowFile(oldPlainSz uint64, newPlainSz uint64) syscall.Errno`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 7119 bytes across 219 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, log, sync, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/file_allocate_truncate.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_allocate_truncate.go -->
