# sources/security-integrity/selinux/libsemanage/tests/test_semanage_store.h

## Purpose
`test_semanage_store.h` declares the CUnit suite hooks and individual test functions for lower-level semanage store tests.

## Important APIs, Types, and Functions
It includes `<CUnit/Basic.h>` and declares `semanage_store_test_init`, `semanage_store_test_cleanup`, `semanage_store_add_tests`, `test_semanage_store_access_check`, `test_semanage_get_lock`, and `test_semanage_nc_sort`.

## Control Flow
There is no executable flow in the header. Its declarations let the CUnit runner register the suite and optionally reference individual test functions.

## State and Persistence Behavior
The header owns no state. Filesystem state is created and removed by `test_semanage_store.c`.

## Dependencies and Integration Points
The include guard is `__TEST_SEMANAGE_STORE_H__`. It connects the store test implementation to the CUnit registry.

## Risks and Test Signals
The extra individual-test declarations increase the surface for declaration drift if function names change. Runtime signals are in `test_semanage_store.c`.
