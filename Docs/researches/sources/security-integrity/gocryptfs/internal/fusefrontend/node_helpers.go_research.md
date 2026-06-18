<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_helpers.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_helpers.go

- Purpose: Provides shared forward-mode helpers for context extraction, node casting, symlink target decryption, size translation, path lookup, and stable child inode creation.
- Important APIs/types/functions: `func toFuseCtx(ctx context.Context) (ctx2 *fuse.Context)`, `func toNode(op fs.InodeEmbedder) *Node`, `func (n *Node) readlink(dirfd int, cName string) (out []byte, errno syscall.Errno)`, `func (n *Node) translateSize(dirfd int, cName string, out *fuse.Attr)`, `func (n *Node) Path() string`, `func (n *Node) rootNode() *RootNode`, `func (n *Node) newChild(ctx context.Context, st *syscall.Stat_t, out *fuse.EntryOut) *fs.Inode`.
- Control flow and state: transforms data through encryption/decryption boundaries. Source size is 2972 bytes across 105 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_helpers.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_helpers.go -->
