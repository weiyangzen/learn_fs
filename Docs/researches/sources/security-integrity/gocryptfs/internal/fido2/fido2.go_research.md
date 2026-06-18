<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fido2/fido2.go -->
# sources/security-integrity/gocryptfs/internal/fido2/fido2.go

- Purpose: Wraps external libfido2 command-line tools to register credentials and derive HMAC secrets for token-assisted unlocking.
- Important APIs/types/functions: `type fidoCommand int`, `const (`, `const relyingPartyID = "gocryptfs"`, `func (fc fidoCommand) String() string`, `func callFidoCommand(command fidoCommand, assertOptions []string, device string, stdin []string) ([]string, error)`, `func Register(device string, userName string) (credentialID []byte)`, `func Secret(device string, assertOptions []string, credentialID []byte, salt []byte) (secret []byte)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; treats invalid internal invariants as fatal/panic conditions; can terminate the process on unrecoverable setup or external command errors. Source size is 3358 bytes across 124 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, encoding/base64, fmt, io, os, os/exec, strings; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/exitcodes, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fido2/fido2.go` and the declarations listed above.
- Risks and review notes: secret input handling must avoid truncation surprises, command injection assumptions, and accidental logging of sensitive material.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fido2/fido2.go -->
