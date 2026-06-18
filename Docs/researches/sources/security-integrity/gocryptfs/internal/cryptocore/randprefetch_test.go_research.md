<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch_test.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/cryptocore, centered on TestRandPrefetch, BenchmarkRandPrefetch. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestRandPrefetch(t *testing.T)`, `func BenchmarkRandPrefetch(b *testing.B)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; is non-persistent test/benchmark code. Source size is 964 bytes across 49 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, compress/flate, runtime, sync, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; shared mutable state needs race-free registration, cleanup, and bounded resource use; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestRandPrefetch, BenchmarkRandPrefetch.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch_test.go -->
