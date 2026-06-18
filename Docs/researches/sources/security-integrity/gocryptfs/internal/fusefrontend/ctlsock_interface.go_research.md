<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/ctlsock_interface.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/ctlsock_interface.go

- Purpose: Implements control-socket path translation for forward mode by walking encrypted directories level by level with diriv-aware name transforms.
- Important APIs/types/functions: `var _ ctlsocksrv.Interface = &RootNode} // Verify that interface is implemented.`, `func (rn *RootNode) EncryptPath(plainPath string) (cipherPath string, err error)`, `func (rn *RootNode) DecryptPath(cipherPath string) (plainPath string, err error)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 3048 bytes across 113 lines, read as part of this work item.
- Dependencies and integration points: standard library: path, path/filepath, strings, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/ctlsocksrv, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/ctlsock_interface.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/ctlsock_interface.go -->
