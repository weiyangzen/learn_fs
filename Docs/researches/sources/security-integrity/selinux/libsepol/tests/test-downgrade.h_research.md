# sources/security-integrity/selinux/libsepol/tests/test-downgrade.h

## Purpose
This header exposes the binary policy downgrade test suite and its file I/O helpers.

## Important APIs, Types, And Functions
It includes CUnit and `policydb.h`, then declares suite hooks `downgrade_test_init()`, `downgrade_test_cleanup()`, `downgrade_add_tests()`, test entry `test_downgrade()`, worker `do_downgrade_test(int mls)`, and helpers `read_binary_policy()` and `write_binary_policy()`.

## Control Flow
The runner registers the downgrade test through `downgrade_add_tests()`. Other code may call the read/write helpers directly with a path and policydb pointer.

## State And Persistence Behavior
No state is declared in the header, but the APIs expose functions that read and write binary policy files.

## Dependencies And Integration Points
It integrates binary policy version tests with the common CUnit runner and policydb serialization APIs.

## Risks And Edge Cases
The helper declarations make file-writing utilities visible beyond the suite; callers must pass initialized policydbs and valid paths.

## Test Signals
Header-level signals are compile-time compatibility and suite registration.
