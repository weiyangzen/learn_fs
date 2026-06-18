<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/chacha.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/chacha.go

- Purpose: Constructs an OpenSSL EVP-backed ChaCha20-Poly1305 AEAD wrapper, verifying the cipher is available at init.
- Important APIs/types/functions: `type stupidChacha20poly1305 struct`, `var _ cipher.AEAD = &stupidChacha20poly1305}`, `var _EVP_chacha20_poly1305 *C.EVP_CIPHER`, `func init()`, `func NewChacha20poly1305(key []byte) cipher.AEAD`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 1465 bytes across 55 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/cipher, log; external/internal modules: golang.org/x/crypto/chacha20poly1305. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/chacha.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/stupidgcm/chacha_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/chacha.go -->
