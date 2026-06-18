# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_assert_that.py

## Purpose
This module tests both the function `assert_that` and the `TestCase.assertThat` method.

## Important APIs, types, and functions
`AssertThatTests` is a shared mixin whose subclasses supply `assert_that_callable`. It tests successful matching, mismatch-to-failure conversion, plain output, message annotation, verbose output, and verbose Unicode formatting. `TestAssertThatFunction` binds to `testtools.assertions.assert_that`; `TestAssertThatMethod` binds to `self.assertThat`.

## Control flow
Custom local matcher and mismatch classes record call order to prove `assertThat` calls `match()` and `describe()` but does not unnecessarily stringify the matcher in non-verbose mode. `assertFails()` captures the framework failure exception and compares it with `DocTestMatches`. `get_error_string()` uses `TracebackContent` to normalize exception output across Python versions.

## State and persistence behavior
No persistence exists. Local call logs are in-memory lists.

## Dependencies and integration points
It depends on `doctest.ELLIPSIS`, `TracebackContent`, `Annotate`, `DocTestMatches`, and `Equals`. It directly protects the public assertion API used throughout testtools and downstream projects.

## Risks and test signals
Assertion failure text is a user-facing contract. Tests cover annotation, verbose formatting, and non-ASCII strings; changes in traceback formatting or exception rendering can affect expectations.
