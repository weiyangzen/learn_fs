# sources/security-integrity/selinux/libsemanage/tests/test_bool.c

## Purpose
CUnit coverage for boolean record, policy, and local transaction APIs.

## Control flow and fixtures
Suite setup creates a test store and writes `test_bool.policy`; cleanup destroys it. Helpers fetch policy booleans, keys, and create/delete local overrides. Tests cover key creation/extraction, compare/compare2, name/value setters, create/clone, policy query/exists/count/iterate/list, and local modify/delete/query/exists/count/iterate/list.

## State and persistence
Policy booleans are read from the test policy. Local boolean changes are only expected to succeed in transaction mode; transactional tests commit and reopen transactions to verify file persistence.

## Risks and signals
Tests intentionally exercise invalid handle state and NULL output arguments for some APIs. `helper_bool_key_extract()` defines unused invalid modes but only runs the valid indexed case, leaving NULL behavior less covered.
