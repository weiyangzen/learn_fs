<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/ausyscall/ausyscall.c -->
# sources/security-integrity/audit-userspace/tools/ausyscall/ausyscall.c

**Purpose**
`ausyscall` maps syscall names to numbers and numbers to names for a selected or detected audit machine architecture, with optional table dumping and exact lookup.

**Important APIs, Types, And Functions**
`usage` exits with command help. `main` parses command-line tokens and calls libaudit APIs `audit_determine_machine`, `audit_detect_machine`, `audit_machine_to_name`, `audit_syscall_to_name`, and `audit_name_to_syscall`. `LAST_SYSCALL` bounds substring lookup to 1400, while `--dump` scans 0..8191.

**Control Flow**
Arguments can include an architecture, syscall number, syscall name, `--dump`, and `--exact`. Numeric tokens become `syscall_num`; architecture names are resolved by libaudit; unsupported/deprecated architecture strings produce explicit messages. If only `uring` is supplied and parsed as `MACH_IO_URING`, it is treated as a syscall name. The tool detects machine type if none was supplied, dumps the table when requested, otherwise performs exact or substring name lookup or number lookup.

**State And Persistence**
The program is stateless and writes results to stdout or errors to stderr.

**Dependencies And Integration Points**
It depends on libaudit’s compiled syscall tables and configured architecture macros such as `WITH_ARM`, `WITH_AARCH64`, and `WITH_RISCV`.

**Risks**
Substring lookup only searches to `LAST_SYSCALL`, so architectures with higher syscall numbers may be incomplete outside dump mode. `strtol` results are not range-validated and non-digit suffixes are not rejected after the leading digit.

**Test Signals**
No direct test is registered here; behavior is usually validated by manual command use and libaudit table tests elsewhere.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/ausyscall/ausyscall.c -->
