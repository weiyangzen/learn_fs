<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/autherr.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/autherr.go

- Purpose: Defines the shared authentication failure error for OpenSSL-backed AEAD wrappers.
- Important APIs/types/functions: `var ErrAuth = fmt.Errorf("stupidgcm: message authentication failed")`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 168 bytes across 9 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/autherr.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/autherr.go -->
