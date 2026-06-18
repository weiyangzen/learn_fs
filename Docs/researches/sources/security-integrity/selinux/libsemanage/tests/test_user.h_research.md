# sources/security-integrity/selinux/libsemanage/tests/test_user.h

## Purpose
`test_user.h` declares lifecycle hooks for the libsemanage user CUnit suite.

## Important APIs, Types, and Functions
It includes `<CUnit/Basic.h>` and declares `user_test_init`, `user_test_cleanup`, and `user_add_tests(CU_pSuite suite)`.

## Control Flow
The file has no executable behavior. The CUnit runner uses it to call into `test_user.c`.

## State and Persistence Behavior
No state is stored here. Test-store state is created, used, and destroyed by the implementation.

## Dependencies and Integration Points
The include guard is `__TEST_USER_H__`; the integration point is the central CUnit suite registration path.

## Risks and Test Signals
Declaration drift is the main risk. Runtime correctness signals come from `test_user.c`.
