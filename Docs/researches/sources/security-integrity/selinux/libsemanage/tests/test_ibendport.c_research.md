# sources/security-integrity/selinux/libsemanage/tests/test_ibendport.c

## Purpose
CUnit coverage for InfiniBand endport policy and local APIs.

## Control flow and fixtures
Setup creates a test store and writes `test_ibendport.policy`. Helpers retrieve policy records/keys and add/delete local overrides. Tests cover policy query/exists/count/iterate/list and local modify/delete/query/exists/count/iterate/list.

## State and persistence
Policy fixtures define three endports with device names, ports, and contexts. Local tests run in transaction mode, commit/reopen for one query path, and verify local counts as records are added/deleted.

## Risks and signals
Iteration tests verify normal traversal, handler error propagation, and handler-requested break. Tests compare device names, ports, and contexts, but record creation/setter unit coverage is likely in separate files outside this subset.
