# sources/security-integrity/selinux/libsemanage/tests/test_semanage_store.c

## Purpose
`test_semanage_store.c` tests lower-level libsemanage store behavior: access checks over store paths and locks, active/trans lock acquisition and release, and netfilter-context sorting through `semanage_nc_sort`.

## Important APIs, Types, and Functions
Suite lifecycle functions are `semanage_store_test_init`, `semanage_store_test_cleanup`, and `semanage_store_add_tests`. Test functions are `test_semanage_store_access_check`, `test_semanage_get_lock`, and `test_semanage_nc_sort`.

The implementation reaches into lower-level libsemanage internals via `handle.h` and `semanage_store.h`, using `semanage_check_init`, `semanage_store_access_check`, `semanage_get_active_lock`, `semanage_release_active_lock`, `semanage_get_trans_lock`, `semanage_release_trans_lock`, and `semanage_nc_sort`. It also directly adjusts `sh->conf->store_path` and `sh->msg_callback`.

## Control Flow
Initialization creates `./test-policy/store/active/modules`, creates a handle, suppresses messages, sets the store path to `"store"`, and initializes store paths with `semanage_check_init(sh, rootpath)`. Cleanup removes the empty module, active, store, and root directories and destroys the handle.

The access test creates a read lock file and repeatedly changes permissions on the store path, read lock, and modules path, asserting the reported access level for no access, read, write, and missing-lock combinations. The lock test acquires active and transaction locks twice to verify reentrant or already-held behavior, releases them, reacquires, and removes lock files. The nc-sort test mmaps `nc_sort_unsorted`, `nc_sort_sorted`, and `nc_sort_malformed`, compares sorted output to the expected buffer, and verifies malformed input fails.

## State and Persistence Behavior
This suite manipulates real filesystem permissions and lock files under `./test-policy`. It uses `mknod`, `chmod`, `remove`, `mkdir`, `rmdir`, `open`, `mmap`, and `munmap`. The test assumes cleanup can remove directories directly, so tests must leave no generated children behind except files removed inside the tests.

## Dependencies and Integration Points
Dependencies include CUnit, POSIX filesystem APIs, `handle.h`, `semanage_store.h`, shared test utilities, and fixture files `nc_sort_unsorted`, `nc_sort_sorted`, and `nc_sort_malformed`. It is an integration point between public handle setup and private store implementation details.

## Risks and Edge Cases
Permission checks can behave differently when tests run as root or under unusual filesystem ACL/mount options. The suite directly modifies internal handle fields, so internal structure changes can break it. `test_semanage_store_access_check` does not restore all permissions between every branch except by applying the next mode, so an early fatal exit can leave awkward local state. `CU_ASSERT_STRING_EQUAL(sorted_buf, good_buf)` assumes mmaped expected data is NUL-terminated or at least safe for C string comparison.

## Test Signals
Strong signals are exact access constants (`-1`, `0`, `SEMANAGE_CAN_READ`, `SEMANAGE_CAN_WRITE`), successful repeated lock acquisition/release, byte-equivalent netfilter context sort output for valid input, and `-1` from malformed netfilter context data.
