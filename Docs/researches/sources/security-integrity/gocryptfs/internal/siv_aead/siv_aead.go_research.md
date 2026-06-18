<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/siv_aead.go -->
# sources/security-integrity/gocryptfs/internal/siv_aead/siv_aead.go

- Purpose: Adapts the jacobsa AES-SIV implementation to Go cipher.AEAD with gocryptfs nonce, overhead, seal/open, and wipe semantics.
- Important APIs/types/functions: `type sivAead struct`, `const (`, `var _ cipher.AEAD = &sivAead}`, `func New(key []byte) cipher.AEAD`, `func new2(keyIn []byte) cipher.AEAD`, `func (s *sivAead) NonceSize() int`, `func (s *sivAead) Overhead() int`, `func (s *sivAead) Seal(dst, nonce, plaintext, authData []byte) []byte`, `func (s *sivAead) Open(dst, nonce, ciphertext, authData []byte) ([]byte, error)`, `func (s *sivAead) Wipe()`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 2879 bytes across 103 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/cipher, log; external/internal modules: github.com/aperturerobotics/jacobsa-crypto/siv. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/siv_aead/siv_aead.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/siv_aead.go -->
