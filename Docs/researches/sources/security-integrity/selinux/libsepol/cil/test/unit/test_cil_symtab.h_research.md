# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_symtab.h

Purpose: Declares the CuTest entry point for CIL symbol-table insertion coverage.

Important APIs and types: Exposes `void test_cil_symtab_insert(CuTest *)` and includes `CuTest.h`.

Control flow: No runtime logic exists. The test runner uses this prototype to register the implementation from `test_cil_symtab.c`.

State and persistence: No state is declared. All tested state is transient CIL database and symbol-table memory created by the implementation.

Dependencies and integration points: It is consumed by the CIL unit-test suite and must remain synchronized with `test_cil_symtab.c`.

Risks: Any rename mismatch breaks compilation or silently drops coverage if suite registration is manually maintained elsewhere.

Test signals: Build success and execution of `test_cil_symtab_insert` confirm this header contract.
