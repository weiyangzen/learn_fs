<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/chacha_test.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/chacha_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/stupidgcm, centered on TestStupidChacha20poly1305. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestStupidChacha20poly1305(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 321 bytes across 21 lines, read as part of this work item.
- Dependencies and integration points: standard library: testing; external/internal modules: golang.org/x/crypto/chacha20poly1305. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/chacha_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestStupidChacha20poly1305.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/chacha_test.go -->
