<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/cipher_suites.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/cipher_suites.go

- Purpose: Reports CPU/OpenSSL cipher-suite capability flags used to choose or display accelerated implementations.
- Important APIs/types/functions: `var (`.
- Control flow and state: transforms data through encryption/decryption boundaries. Source size is 756 bytes across 29 lines, read as part of this work item.
- Dependencies and integration points: standard library: runtime; external/internal modules: golang.org/x/sys/cpu. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/cipher_suites.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/cipher_suites.go -->
