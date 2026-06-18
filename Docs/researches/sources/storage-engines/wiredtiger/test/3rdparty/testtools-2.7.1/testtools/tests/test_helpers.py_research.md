# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_helpers.py

## Purpose
This module tests the stack-hiding helper functions from `testtools.tests.helpers`.

## Important APIs, types, and functions
`TestStackHiding` uses `FullStackRunTest`, `hide_testtools_stack`, and `is_stack_hidden`. It has two tests: one for setting the flag true and one for setting it false.

## Control flow
`setUp()` registers cleanup to restore the original stack hiding state. Each test toggles the flag and checks that the observed value matches.

## State and persistence behavior
The tested state is the global `StackLinesContent.HIDE_INTERNAL_STACK` flag. Cleanup prevents leakage across tests.

## Dependencies and integration points
It depends on the helper module and `testtools.TestCase`. It protects the shared behavior used by many tests through `FullStackRunTest`.

## Risks and test signals
Because the flag is global, missing cleanup would cause cross-test contamination. These tests are simple but valuable for detecting helper regressions.
