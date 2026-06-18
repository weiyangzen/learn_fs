<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_open_create.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_open_create.go

- Purpose: Implements forward-mode open/create flag rewriting, write-only permission workaround integration, long-name sidecar creation, and file-handle construction.
- Important APIs/types/functions: `func mangleOpenCreateFlags(flags uint32) (newFlags int)`, `func (n *Node) Open(ctx context.Context, flags uint32) (fh fs.FileHandle, fuseFlags uint32, errno syscall.Errno)`, `func (n *Node) Create(ctx context.Context, name string, flags uint32, mode uint32, out *fuse.EntryOut) (inode *fs.Inode, fh fs....`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup. Source size is 4548 bytes across 140 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, os, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_open_create.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_open_create.go -->
