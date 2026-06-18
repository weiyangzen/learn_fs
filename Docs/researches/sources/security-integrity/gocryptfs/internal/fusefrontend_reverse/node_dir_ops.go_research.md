<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_dir_ops.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_dir_ops.go

- Purpose: Implements reverse-mode readdir by reading plaintext entries, filtering exclusions, and synthesizing encrypted directory entries plus virtual metadata files.
- Important APIs/types/functions: `func (n *Node) Readdir(ctx context.Context) (stream fs.DirStream, errno syscall.Errno)`, `func (n *Node) readdirPlaintextnames(entries []fuse.DirEntry) (stream fs.DirStream, errno syscall.Errno)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 3764 bytes across 119 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, fmt, syscall; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/configfile, github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_dir_ops.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_dir_ops.go -->
