# sources/security-integrity/selinux/libsemanage/tests/test_handle.c

## Purpose
CUnit coverage for semanage handle lifecycle and configuration-facing operations.

## Control flow and fixtures
Setup creates a test store and writes `test_handle.policy`. Tests cover handle create/destroy, connect/disconnect, transaction begin/commit, connection-state checks, access checks, managed-store detection, MLS enabled queries, message callback installation/removal, root setters, and store selection for valid/invalid connection types.

## State and persistence
Uses shared test helpers to create handles at null, raw handle, connected, and transaction levels. Store selection tests connect to direct stores and reject policy server modes.

## Risks and signals
Callback test verifies exactly one emitted error message from an invalid commit. Root changes are global process state, so ordering with other suites matters if tests are parallelized.
