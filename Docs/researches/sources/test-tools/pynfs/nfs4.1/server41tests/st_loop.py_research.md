# sources/test-tools/pynfs/nfs4.1/server41tests/st_loop.py

Purpose: deliberately tiny dependency-loop fixture for the test harness.

Important APIs/types/functions: `test1` has `CODE: XXX1` and `DEPEND: XXX2`; `test2` has `CODE: XXX2` and `DEPEND: XXX1`.

Control flow: both test bodies immediately return. The interesting behavior is entirely in `testmod._runtree`, which should detect circular dependency wait states when either test is selected.

State and persistence behavior: no NFS operations, external state, or persistence.

Dependencies/integration: integrates only through docstring metadata parsed by `testmod.createtests`.

Risks and test signals: the module is not a protocol test; it is useful for validating dependency-cycle handling. If run accidentally as a real protocol test, pass/fail meaning is limited.
