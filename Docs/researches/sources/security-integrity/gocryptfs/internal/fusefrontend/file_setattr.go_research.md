<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_setattr.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/file_setattr.go

- Purpose: Applies chmod/chown/timestamps/truncate through an open encrypted file handle while holding content locks.
- Important APIs/types/functions: `func (f *File) Setattr(ctx context.Context, in *fuse.SetAttrIn, out *fuse.AttrOut) (errno syscall.Errno)`, `func (f *File) setAttr(ctx context.Context, in *fuse.SetAttrIn) (errno syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths. Source size is 1631 bytes across 86 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/file_setattr.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_setattr.go -->
