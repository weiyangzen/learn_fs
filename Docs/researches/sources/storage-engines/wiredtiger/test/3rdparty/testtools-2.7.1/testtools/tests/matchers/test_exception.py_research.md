# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/matchers/test_exception.py

## Purpose
This module tests exception matchers and callable-raising matchers.

## Important APIs, types, and functions
`make_error()` captures `sys.exc_info()` for a raised exception. Interface tests cover `MatchesException` with an exception instance, an exception type, a regex over exception text, and a matcher over exception text. `TestRaisesInterface` and `TestRaisesExceptionMatcherInterface` cover `Raises`. `TestRaisesBaseTypes` verifies handling of `KeyboardInterrupt`. `TestRaisesConvenience` covers the `raises()` helper.

## Control flow
`make_error()` raises and catches the target exception type, returning the captured tuple. Matchers compare type inheritance, instance arguments, regex matches, and nested matcher results. `Raises.match()` is tested against callables that raise, return normally, or raise base exceptions that should propagate unless explicitly matched.

## State and persistence behavior
No persistent state exists. Tests create exception tuples and local callables.

## Dependencies and integration points
It depends on `sys`, `AfterPreprocessing`, `Equals`, `_exception` matchers, `FullStackRunTest`, and `TestMatchersInterface`. These matchers are used in many other test modules to assert failure and error behavior.

## Risks and test signals
Exception `repr` changed around Python 3.7, and the tests account for that. The base-exception path is important: default `Raises()` should not swallow `KeyboardInterrupt`, while explicit matching should. This protects process-control semantics.
