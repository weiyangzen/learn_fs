<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/correctness_test.go -->
# sources/security-integrity/gocryptfs/internal/siv_aead/correctness_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/siv_aead, centered on TestKeyLens, TestK32, TestK64. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestKeyLens(t *testing.T)`, `func TestK32(t *testing.T)`, `func TestK64(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 4044 bytes across 149 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, encoding/hex, testing; external/internal modules: github.com/aperturerobotics/jacobsa-crypto/siv. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/siv_aead/correctness_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestKeyLens, TestK32, TestK64.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/correctness_test.go -->
