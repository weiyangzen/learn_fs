# sources/test-tools/ltp/testcases/kernel/syscalls/execv/execv01.c

Purpose: Tests successful `execv()` replacement using an explicit argv vector and resolved helper path.

Important APIs/types/functions: `tst_get_path`, `SAFE_FORK`, `execv(path, args)`, `TEST()`, and LTP child reinitialization.

Control flow: The parent resolves `execv01_child`, forks, and the child calls `execv` with `argv[0]` and a `canary` argument.

State and persistence behavior: The argv vector is transient state; no files are modified by the test itself.

Dependencies and integration points: Integrated with the sibling child helper and LTP resource path lookup.

Risks and test signals: The only success path is the helper running and reporting `TPASS`; any returned exec call is a parent-test failure.
