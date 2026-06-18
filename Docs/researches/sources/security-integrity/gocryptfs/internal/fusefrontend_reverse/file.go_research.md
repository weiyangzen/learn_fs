<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file.go

- Purpose: Implements reverse-mode file reads by synthesizing ciphertext from plaintext backing file data at requested ciphertext offsets.
- Important APIs/types/functions: `type File struct`, `func (f *File) Read(ctx context.Context, buf []byte, ioff int64) (resultData fuse.ReadResult, errno syscall.Errno)`, `func (f *File) Release(context.Context) syscall.Errno`, `func (f *File) Lseek(ctx context.Context, off uint64, whence uint32) (uint64, syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries. Source size is 1946 bytes across 82 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, context, os, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/contentenc. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file.go -->
