<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/nonce.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/nonce.go

- Purpose: Provides secure random byte and uint64 helpers plus nonce generation backed by the package-level prefetcher.
- Important APIs/types/functions: `type nonceGenerator struct`, `func RandBytes(n int) []byte`, `func RandUint64() uint64`, `func (n *nonceGenerator) Get() []byte`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions. Source size is 738 bytes across 35 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/rand, encoding/binary, log. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/nonce.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/nonce.go -->
