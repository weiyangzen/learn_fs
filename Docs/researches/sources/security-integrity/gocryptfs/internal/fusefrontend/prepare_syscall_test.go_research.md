<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/prepare_syscall_test.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/prepare_syscall_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/fusefrontend, centered on TestPrepareAtSyscall, TestPrepareAtSyscallPlaintextnames. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestPrepareAtSyscall(t *testing.T)`, `func TestPrepareAtSyscallPlaintextnames(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 3762 bytes across 174 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, strings, syscall, testing; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/tests/test_helpers. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/prepare_syscall_test.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestPrepareAtSyscall, TestPrepareAtSyscallPlaintextnames.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/prepare_syscall_test.go -->
