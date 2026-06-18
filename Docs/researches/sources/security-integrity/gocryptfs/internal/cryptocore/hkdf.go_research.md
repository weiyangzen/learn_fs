<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/hkdf.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/hkdf.go

- Purpose: Provides HKDF-SHA256 domain-separated key derivation for filename, GCM, SIV, and XChaCha20-Poly1305 uses.
- Important APIs/types/functions: `const (`, `func hkdfDerive(masterkey []byte, info string, outLen int) []byte`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 845 bytes across 28 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/hkdf, crypto/sha256, log. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/hkdf.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/cryptocore/hkdf_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/hkdf.go -->
