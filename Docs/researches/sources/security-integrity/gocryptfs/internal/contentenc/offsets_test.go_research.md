<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/offsets_test.go -->
# sources/security-integrity/gocryptfs/internal/contentenc/offsets_test.go

- Purpose: Exercises size and offset conversion monotonicity over a small range, printing boundary points where ciphertext/header overhead changes the mapping.
- Important APIs/types/functions: `func TestSizeToSize(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; is non-persistent test/benchmark code. Source size is 1436 bytes across 54 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, testing; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/cryptocore. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/contentenc/offsets_test.go` and the declarations listed above.
- Risks and review notes: test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestSizeToSize.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/offsets_test.go -->
