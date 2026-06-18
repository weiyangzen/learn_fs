<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/nfc_test.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/nfc_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/nametransform, centered on TestNFD2NFC. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestNFD2NFC(t *testing.T)`.
- Control flow and state: participates in directory-IV based name encryption state; transforms data through encryption/decryption boundaries; is non-persistent test/benchmark code. Source size is 793 bytes across 30 lines, read as part of this work item.
- Dependencies and integration points: standard library: strconv, testing; external/internal modules: golang.org/x/text/unicode/norm. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/nfc_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestNFD2NFC.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/nfc_test.go -->
