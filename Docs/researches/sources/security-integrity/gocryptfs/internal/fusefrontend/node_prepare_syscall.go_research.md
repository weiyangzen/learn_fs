<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_prepare_syscall.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_prepare_syscall.go

- Purpose: Centralizes forward-mode conversion from plaintext child names to backing directory fd plus ciphertext name for symlink-safe *at syscalls.
- Important APIs/types/functions: `func (n *Node) prepareAtSyscall(child string) (dirfd int, cName string, errno syscall.Errno)`, `func (n *Node) prepareAtSyscallMyself() (dirfd int, cName string, errno syscall.Errno)`.
- Control flow and state: uses descriptor-relative syscalls to avoid path races and symlink traversal; participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 2950 bytes across 119 lines, read as part of this work item.
- Dependencies and integration points: standard library: syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog, github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_prepare_syscall.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_prepare_syscall.go -->
