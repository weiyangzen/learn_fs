<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/perms.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/perms.go

- Purpose: Documents and defines permission constants for internal diriv and long-name metadata files.
- Important APIs/types/functions: `const (`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 912 bytes across 27 lines, read as part of this work item.
- Dependencies and integration points: No Go imports; dependencies are shell/make tooling or package-local constants only. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/perms.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/perms.go -->
