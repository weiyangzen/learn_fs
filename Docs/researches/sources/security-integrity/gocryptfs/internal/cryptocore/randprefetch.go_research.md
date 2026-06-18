<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch.go

- Purpose: Maintains a background random-byte prefetch buffer so frequent nonce generation does not synchronously hit crypto/rand for every nonce.
- Important APIs/types/functions: `type randPrefetcherT struct`, `const prefetchN = 512`, `var randPrefetcher randPrefetcherT`, `func init()`, `func (r *randPrefetcherT) read(want int) (out []byte)`, `func (r *randPrefetcherT) refillWorker()`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; treats invalid internal invariants as fatal/panic conditions. Source size is 1150 bytes across 56 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, log, sync. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; shared mutable state needs race-free registration, cleanup, and bounded resource use.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch.go -->
