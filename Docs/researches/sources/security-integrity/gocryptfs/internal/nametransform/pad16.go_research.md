<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/pad16.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/pad16.go

- Purpose: Pads arbitrary names to AES block boundaries and removes padding during decryption with corruption checks.
- Important APIs/types/functions: `func pad16(orig []byte) (padded []byte)`, `func unPad16(padded []byte) ([]byte, error)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; treats invalid internal invariants as fatal/panic conditions. Source size is 1686 bytes across 65 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/aes, errors, fmt, log. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/pad16.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/pad16.go -->
