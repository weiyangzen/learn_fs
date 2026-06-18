# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_tree.h

Purpose: Declares CuTest entry points for CIL tree initialization tests.

Important APIs and types: Exposes `test_cil_tree_node_init(CuTest *)` and `test_cil_tree_init(CuTest *)`.

Control flow: No executable logic exists. It lets the suite driver compile against the implementations in `test_cil_tree.c`.

State and persistence: No state is owned. The implementations allocate transient tree structures.

Dependencies and integration points: Depends only on `CuTest.h` and is part of the CIL unit-test build.

Risks: Header/implementation drift would break the unit-test target or omit a test during suite registration.

Test signals: Compilation and invocation of both tests validate the header surface.
