<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/rpath.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/rpath.go

- Purpose: Decrypts reverse-mode ciphertext paths back to plaintext paths, derives deterministic directory IVs, and opens plaintext backing directories safely.
- Important APIs/types/functions: `func (rfs *RootNode) rDecryptName(cName string, dirIV []byte, pDir string) (pName string, err error)`, `func (rn *RootNode) decryptPath(cPath string) (string, error)`, `func (rn *RootNode) deriveDirIV(cPath string) []byte`, `func (rn *RootNode) openBackingDir(cPath string) (dirfd int, pPath string, err error)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 4105 bytes across 124 lines, read as part of this work item.
- Dependencies and integration points: standard library: encoding/base64, log, path/filepath, strings, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/pathiv, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/rpath.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/rpath.go -->
