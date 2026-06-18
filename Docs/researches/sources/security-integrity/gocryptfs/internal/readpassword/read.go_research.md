<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/read.go -->
# sources/security-integrity/gocryptfs/internal/readpassword/read.go

- Purpose: Implements password acquisition from passfiles, terminal, stdin, or external commands, with once/twice confirmation flows.
- Important APIs/types/functions: `const (`, `func Once(extpass []string, passfile []string, prompt string) ([]byte, error)`, `func Twice(extpass []string, passfile []string) ([]byte, error)`, `func readPasswordTerminal(prompt string) ([]byte, error)`, `func readPasswordStdin(prompt string) ([]byte, error)`, `func readPasswordExtpass(extpass []string) ([]byte, error)`, `func readLineUnbuffered(r io.Reader) (l []byte, err error)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions. Source size is 4321 bytes across 168 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, fmt, io, os, os/exec, strings; external/internal modules: golang.org/x/term, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/readpassword/read.go` and the declarations listed above.
- Risks and review notes: secret input handling must avoid truncation surprises, command injection assumptions, and accidental logging of sensitive material.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/read.go -->
