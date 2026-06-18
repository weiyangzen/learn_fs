<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_linux.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_linux.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend_reverse covering the node_xattr_linux.go slice of that package.
- Important APIs/types/functions: `const noSuchAttributeError = syscall.ENODATA`, `func (n *Node) getXAttr(cAttr string) (out []byte, errno syscall.Errno)`, `func (n *Node) listXAttr() (out []string, errno syscall.Errno)`.
- Control flow and state: maps extended attributes between plaintext API names and backing storage names. Source size is 976 bytes across 44 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_linux.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_linux.go -->
