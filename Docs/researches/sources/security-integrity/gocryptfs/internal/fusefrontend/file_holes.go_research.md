<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_holes.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/file_holes.go

- Purpose: Handles sparse-file behavior, zero padding before holes, and SEEK_DATA/SEEK_HOLE translation between plaintext and ciphertext block layouts.
- Important APIs/types/functions: `func (f *File) writePadHole(targetOff int64) syscall.Errno`, `func (f *File) zeroPad(plainSize uint64) syscall.Errno`, `func (f *File) Lseek(ctx context.Context, off uint64, whence uint32) (uint64, syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries. Source size is 4529 bytes across 129 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, runtime, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/file_holes.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_holes.go -->
