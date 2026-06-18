# sources/security-integrity/selinux/libsepol/tests/helpers.h

## Purpose
`helpers.h` declares shared test helpers and adjusts selected CUnit fatal assertions for static analysis.

## APIs and Integration
It declares `test_load_policy()` and `test_find_decl_by_sym()`. Under `__CHECKER__`, selected `CU_*_FATAL` macros also call `assert()` so static analyzers understand the control flow. It includes policydb, conditional policy, and CUnit definitions.

## Risks and Test Signals
The include guard name `__COMMON_H__` is generic and could collide. Runtime behavior remains CUnit-defined unless `__CHECKER__` is set. Build coverage with and without static-analysis settings plus policy-loading suites validate it.
