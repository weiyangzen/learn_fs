<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/badname.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/badname.go

- Purpose: Handles badname compatibility by searching for matching ciphertext names when plaintext names contain legacy or ambiguous encodings.
- Important APIs/types/functions: `const (`, `func (be *NameTransform) EncryptAndHashBadName(name string, iv []byte, dirfd int) (cName string, err error)`, `func (n *NameTransform) decryptBadname(cipherName string, iv []byte) (string, error)`, `func (n *NameTransform) HaveBadnamePatterns() bool`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 3084 bytes across 92 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/aes, path/filepath, strings, syscall; external/internal modules: golang.org/x/sys/unix, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/badname.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/badname.go -->
