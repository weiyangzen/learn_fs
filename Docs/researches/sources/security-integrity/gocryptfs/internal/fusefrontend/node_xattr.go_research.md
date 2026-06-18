<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr.go

- Purpose: Implements frontend xattr policy: optional no-xattr mode, capability suppression, ACL passthrough, encrypted xattr names/values, and list filtering.
- Important APIs/types/functions: `var xattrStorePrefix = "user.gocryptfs."`, `var xattrCapability = "security.capability"`, `func isAcl(attr string) bool`, `func (n *Node) Getxattr(ctx context.Context, attr string, dest []byte) (uint32, syscall.Errno)`, `func (n *Node) Setxattr(ctx context.Context, attr string, data []byte, flags uint32) syscall.Errno`, `func (n *Node) Removexattr(ctx context.Context, attr string) syscall.Errno`, `func (n *Node) Listxattr(ctx context.Context, dest []byte) (uint32, syscall.Errno)`.
- Control flow and state: transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 4835 bytes across 172 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, context, strings, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr.go -->
