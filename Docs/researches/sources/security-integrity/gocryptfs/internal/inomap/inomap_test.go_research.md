<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/inomap_test.go -->
# sources/security-integrity/gocryptfs/internal/inomap/inomap_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/inomap, centered on TestTranslate, TestTranslateStress, TestSpill, TestUniqueness, BenchmarkTranslateSingleDev, BenchmarkTranslateManyDevs. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `const (`, `func TestTranslate(t *testing.T)`, `func TestTranslateStress(t *testing.T)`, `func TestSpill(t *testing.T)`, `func TestUniqueness(t *testing.T)`, `func BenchmarkTranslateSingleDev(b *testing.B)`, `func BenchmarkTranslateManyDevs(b *testing.B)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 3231 bytes across 169 lines, read as part of this work item.
- Dependencies and integration points: standard library: sync, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/inomap/inomap_test.go` and the declarations listed above.
- Risks and review notes: shared mutable state needs race-free registration, cleanup, and bounded resource use; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestTranslate, TestTranslateStress, TestSpill, TestUniqueness, BenchmarkTranslateSingleDev, BenchmarkTranslateManyDevs.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/inomap_test.go -->
