<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_darwin.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_darwin.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend covering the node_xattr_darwin.go slice of that package.
- Important APIs/types/functions: `const noSuchAttributeError = syscall.ENOATTR`, `func filterXattrSetFlags(flags int) int`, `func (n *Node) getXAttr(cAttr string) (out []byte, errno syscall.Errno)`, `func (n *Node) setXAttr(context *fuse.Context, cAttr string, cData []byte, flags uint32) (errno syscall.Errno)`, `func (n *Node) removeXAttr(cAttr string) (errno syscall.Errno)`, `func (n *Node) listXAttr() (out []string, errno syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; maps extended attributes between plaintext API names and backing storage names. Source size is 3029 bytes across 111 lines, read as part of this work item.
- Dependencies and integration points: standard library: syscall; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_darwin.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_darwin.go -->
