# sources/test-tools/strace/src/linux/ia64/shuffle_scno.c

Purpose: translates raw `ia64` syscall numbers into the table index space used by strace.

Important APIs/types/functions: shuffle_scno_pers; notable register references include none in this file.

Control flow: generic dispatch calls `shuffle_scno_pers`; implementations may leave native numbers unchanged, delegate to compat helpers, or xor/add a base offset after static assertions.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on syscall table size/base-number constants and personality id.

Risks/test signals: wrong shuffling dispatches to the wrong table; test boundary syscall numbers and personality-specific tables.

Source-read signal: reviewed complete local file (11 lines).
