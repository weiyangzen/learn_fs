# sources/test-tools/strace/src/linux/generic/syscallent_base_nr.h

Purpose: defines the base syscall-number offset used when an architecture table is shifted away from zero.

Important APIs/types/functions: syscallent_base_nr.h; notable register references include none in this file.

Control flow: included by arch definitions and shuffle logic so raw syscall numbers map to compact table indexes.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on syscall table generation and architecture ABI base numbers.

Risks/test signals: validate static assertions and first/last syscall dispatch on the architecture.

Source-read signal: reviewed complete local file (1 lines).
