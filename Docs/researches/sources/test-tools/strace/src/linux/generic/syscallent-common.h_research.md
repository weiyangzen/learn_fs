# sources/test-tools/strace/src/linux/generic/syscallent-common.h

Purpose: provides `generic` helper logic for `syscallent-common.h`.

Important APIs/types/functions: BASE_NR; notable register references include none in this file.

Control flow: called or included by generic strace Linux backend code.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on the surrounding strace architecture contracts.

Risks/test signals: compile and run architecture trace coverage for this helper.

Source-read signal: reviewed complete local file (58 lines).
