<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr.go

- Purpose: Synthesizes reverse-mode encrypted xattr reads and xattr name listings from plaintext backing xattrs.
- Important APIs/types/functions: `var xattrStorePrefix = "user.gocryptfs."`, `func isAcl(attr string) bool`, `func (n *Node) Getxattr(ctx context.Context, attr string, dest []byte) (uint32, syscall.Errno)`, `func (n *Node) Listxattr(ctx context.Context, dest []byte) (uint32, syscall.Errno)`.
- Control flow and state: transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 2359 bytes across 90 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, context, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/pathiv. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr.go -->
