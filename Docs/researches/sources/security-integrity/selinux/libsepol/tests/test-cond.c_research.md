# sources/security-integrity/selinux/libsepol/tests/test-cond.c

## Purpose
This CUnit suite tests conditional expression equality in expanded policydbs.

## Important APIs, Types, And Functions
Important functions are `cond_test_init()`, `cond_test_cleanup()`, `test_cond_expr_equal()`, and `cond_add_tests()`. It uses `policydb_t basemod`, `policydb_t base_expanded`, `test_load_policy()`, `link_modules()`, `expand_module()`, and `cond_expr_equal()`.

## Control Flow
Initialization creates the expanded policydb, loads `test-cond/refpolicy-base.conf`, links the base, expands it, and leaves `base_expanded.cond_list` ready. The test nests two loops over every conditional node: a node must equal itself and not equal any distinct node.

## State And Persistence Behavior
The suite owns two static policydbs for the lifetime of the CUnit suite and destroys them in cleanup. It does not write external files.

## Dependencies And Integration Points
It depends on parser helpers, linker, expander, and the conditional module. The policy fixture provides enough conditionals to make equality checks meaningful.

## Risks And Edge Cases
The test assumes distinct conditional nodes are not structurally equal. If two policy expressions are intentionally identical but allocated as separate nodes, this test would treat equality as a bug.

## Test Signals
The registered CUnit test `cond_expr_equal` fails on load/link/expand errors or incorrect equality behavior.
