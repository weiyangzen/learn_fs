<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/stdin_test.go -->
# sources/security-integrity/gocryptfs/internal/readpassword/stdin_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/readpassword, centered on TestStdin, TestStdinEof, TestStdinEmpty. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestStdin(t *testing.T)`, `func TestStdinEof(t *testing.T)`, `func TestStdinEmpty(t *testing.T)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions; can terminate the process on unrecoverable setup or external command errors; is non-persistent test/benchmark code. Source size is 2621 bytes across 120 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, os, os/exec, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/readpassword/stdin_test.go` and the declarations listed above.
- Risks and review notes: secret input handling must avoid truncation surprises, command injection assumptions, and accidental logging of sensitive material; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestStdin, TestStdinEof, TestStdinEmpty.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/stdin_test.go -->
