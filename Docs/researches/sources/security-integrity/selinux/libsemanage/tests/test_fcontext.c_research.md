# sources/security-integrity/selinux/libsemanage/tests/test_fcontext.c

## Purpose
CUnit coverage for file-context record, policy, and local APIs.

## Control flow and fixtures
Setup creates the test store, writes `test_fcontext.policy`, and manually writes three file_contexts lines into `test-policy/store/active/file_contexts`. Tests cover compare ordering, keys, expression/type/context setters, type-string names, create/clone, policy query/exists/count/iterate/list, and local modify/delete/query/exists/count/iterate/list.

## State and persistence
Local fcontext changes are rejected in connected mode and accepted in transactions. Transaction tests commit and reopen before checking local query persistence.

## Risks and signals
The fixture directly writes the active file_contexts file, so failures can indicate store layout drift. Tests cover nonexistent expression/type combinations and invalid handle/list arguments, but not parser malformed-line behavior.
