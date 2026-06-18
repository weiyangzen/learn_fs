<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/ctlsock_interface.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/ctlsock_interface.go

- Purpose: Implements reverse-mode control-socket path translation between plaintext source paths and synthesized ciphertext paths.
- Important APIs/types/functions: `var _ ctlsocksrv.Interface = &RootNode}`, `func (rn *RootNode) EncryptPath(plainPath string) (string, error)`, `func (rn *RootNode) DecryptPath(cipherPath string) (string, error)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 1169 bytes across 42 lines, read as part of this work item.
- Dependencies and integration points: standard library: path/filepath, strings; external/internal modules: golang.org/x/sys/unix, github.com/rfjakob/gocryptfs/v2/internal/ctlsocksrv. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/ctlsock_interface.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/ctlsock_interface.go -->
