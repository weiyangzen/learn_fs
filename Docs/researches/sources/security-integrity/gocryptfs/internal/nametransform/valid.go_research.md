<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/valid.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/valid.go

- Purpose: Validates plaintext file names against empty, slash-containing, dot, and dot-dot forms.
- Important APIs/types/functions: `func IsValidName(name string) error`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 739 bytes across 28 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, strings. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/valid.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/valid.go -->
