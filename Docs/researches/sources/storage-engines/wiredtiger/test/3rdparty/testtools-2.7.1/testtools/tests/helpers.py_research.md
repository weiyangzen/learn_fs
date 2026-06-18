# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/helpers.py

## Purpose
This module supplies shared test utilities used across the testtools self-test suite. It provides a logging result double, stack-hiding controls, a custom `RunTest` that disables stack hiding, structured event matchers, content text matching, and a helper to raise exceptions from expression contexts.

## Important APIs, types, and functions
`LoggingResult` subclasses `TestResult` and appends result protocol events to an external list. `an_exc_info` is a captured exception tuple used by content tests. `is_stack_hidden()`, `hide_testtools_stack()`, and `run_with_stack_hidden()` manipulate `StackLinesContent.HIDE_INTERNAL_STACK`. `FullStackRunTest` overrides `_run_user` to run with stack hiding disabled. `MatchesEvents` recursively turns nested structures into matcher trees. `AsText` preprocesses `Content.as_text()` before applying a matcher. `raise_(exception)` raises a supplied exception.

## Control flow
`LoggingResult` logs each result method before delegating to the base class, preserving real result behavior while exposing an event list for assertions. Stack helpers save the global flag, mutate it, and restore it in `finally`. `MatchesEvents.match()` recursively maps expected tuples/lists/dicts to `MatchesListwise` and `MatchesDict`, with existing matchers passed through.

## State and persistence behavior
The module mutates only in-memory state: the global stack hiding flag and caller-provided event lists. `an_exc_info` intentionally captures a reusable exception tuple.

## Dependencies and integration points
It depends on `testtools.TestResult`, `testtools.content.StackLinesContent`, core matchers, and `testtools.runtest.RunTest`. Many test modules set `run_tests_with = FullStackRunTest` to expose full tracebacks in assertions.

## Risks and test signals
`LoggingResult` is marked deprecated because event attributes can be nondeterministic across Python versions. `MatchesEvents` is convenient but not a general deep matcher; it treats any object with `match` as a matcher. Stack hiding is global and must be restored by callers; `test_helpers.py` validates this behavior.
