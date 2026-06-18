<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/passfile.go -->
# sources/security-integrity/gocryptfs/internal/readpassword/passfile.go

- Purpose: Reads password material from one or more files, using only the first newline-delimited line from each passfile.
- Important APIs/types/functions: `func readPassFileConcatenate(passfileSlice []string) (result []byte, err error)`, `func readPassFile(passfile string) ([]byte, error)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions. Source size is 1598 bytes across 53 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, fmt, os; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/readpassword/passfile.go` and the declarations listed above.
- Risks and review notes: secret input handling must avoid truncation surprises, command injection assumptions, and accidental logging of sensitive material.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/readpassword/passfile_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/passfile.go -->
