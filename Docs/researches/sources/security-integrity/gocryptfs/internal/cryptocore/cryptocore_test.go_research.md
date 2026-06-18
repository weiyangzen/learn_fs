<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore_test.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/cryptocore, centered on TestCryptoCoreNew, TestNewPanic. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestCryptoCoreNew(t *testing.T)`, `func TestNewPanic(t *testing.T)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 812 bytes across 42 lines, read as part of this work item.
- Dependencies and integration points: standard library: testing; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/stupidgcm. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestCryptoCoreNew, TestNewPanic.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore_test.go -->
