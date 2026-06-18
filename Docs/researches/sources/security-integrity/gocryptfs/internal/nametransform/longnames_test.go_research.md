<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/longnames_test.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/longnames_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/nametransform, centered on TestIsLongName, TestRemoveLongNameSuffix, TestLongNameMax. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestIsLongName(t *testing.T)`, `func TestRemoveLongNameSuffix(t *testing.T)`, `func newLognamesTestInstance(longNameMax uint8) *NameTransform`, `func TestLongNameMax(t *testing.T)`.
- Control flow and state: handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; is non-persistent test/benchmark code. Source size is 1944 bytes across 72 lines, read as part of this work item.
- Dependencies and integration points: standard library: strings, testing; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/contentenc, github.com/rfjakob/gocryptfs/v2/internal/cryptocore. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/longnames_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestIsLongName, TestRemoveLongNameSuffix, TestLongNameMax.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/longnames_test.go -->
