# sources/test-tools/strace/src/linux/generic/check_scno.c

Purpose: performs generic syscall-number range validation before table dispatch.

Important APIs/types/functions: arch_check_scno; notable register references include none in this file.

Control flow: checks `tcp->scno` against the active personality table size and lets the generic decoder handle unknown or out-of-range calls consistently.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on active personality syscall table metadata and `struct tcb`.

Risks/test signals: off-by-one range checks affect unknown syscall rendering; test boundary syscall numbers.

Source-read signal: reviewed complete local file (13 lines).
