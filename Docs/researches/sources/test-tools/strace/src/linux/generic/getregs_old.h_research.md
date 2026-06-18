# sources/test-tools/strace/src/linux/generic/getregs_old.h

Purpose: provides compatibility definitions for older register-fetch paths.

Important APIs/types/functions: getregs_old.h; notable register references include none in this file.

Control flow: no direct runtime flow; included by generic register code when old ptrace register APIs are needed.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on architecture/user register headers and generic register-fetch code.

Risks/test signals: compile old-kernel compatibility configurations and run register fetch tests.

Source-read signal: reviewed complete local file (8 lines).
