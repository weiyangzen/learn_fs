# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/fchown05.c

Purpose: verifies root can set arbitrary numeric uid/gid combinations with `fchown(2)`, including owner-only, group-only, and no-op cases.

Important APIs/types/functions: `FCHOWN`, `SAFE_OPEN`, `SAFE_FSTAT`, `TST_EXP_PASS`, and compatibility header `compat_tst_16.h`.

Control flow: setup opens `testfile`. Each table case calls `FCHOWN(fd, uid, gid)` with values or `-1`, computes expected uid/gid from the previous effective state when an argument is `-1`, and verifies `fstat` ownership.

State/persistence behavior: ownership changes accumulate across table cases; expected values intentionally depend on prior case state.

Dependencies/integration: root and tempdir required. Numeric ids may not correspond to local accounts, which is valid for root `chown` semantics.

Risks/test signals: the expected-value logic depends on case order, especially the first non-`-1` state. Failure indicates ownership did not match requested numeric ids.
