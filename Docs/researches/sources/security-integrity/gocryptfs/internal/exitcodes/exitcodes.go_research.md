<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/exitcodes/exitcodes.go -->
# sources/security-integrity/gocryptfs/internal/exitcodes/exitcodes.go

- Purpose: Centralizes stable process exit codes and a small typed error wrapper that carries an exit status.
- Important APIs/types/functions: `type Err struct`, `const (`, `func NewErr(msg string, code int) Err`, `func Exit(err error)`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions; can terminate the process on unrecoverable setup or external command errors. Source size is 3052 bytes across 100 lines, read as part of this work item.
- Dependencies and integration points: standard library: errors, os. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/exitcodes/exitcodes.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/exitcodes/exitcodes.go -->
