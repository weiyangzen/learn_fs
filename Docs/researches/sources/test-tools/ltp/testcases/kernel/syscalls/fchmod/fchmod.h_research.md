# sources/test-tools/ltp/testcases/kernel/syscalls/fchmod/fchmod.h

Purpose: shared constants for the `fchmod` test cases.

Important APIs/types/functions: preprocessor definitions `FILE_MODE`, `DIR_MODE`, `PERMS`, `TESTFILE`, and `TESTDIR`.

Control flow: header guard `FCHMOD_H` prevents double inclusion. No functions or executable code are defined.

State/persistence behavior: no state. It centralizes file and directory names and mode masks used by multiple tests.

Dependencies/integration: included by the `fchmod*.c` tests to keep permission constants consistent.

Risks/test signals: risk is limited to shared constant drift. A wrong mode macro affects several tests' expectations.
