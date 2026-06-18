<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/hkdf_test.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/hkdf_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/cryptocore, centered on TestHkdfDerive. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `type hkdfTestCase struct`, `func TestHkdfDerive(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; is non-persistent test/benchmark code. Source size is 1467 bytes across 47 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, encoding/hex, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/hkdf_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestHkdfDerive.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/hkdf_test.go -->
