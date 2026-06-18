# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/__init__.py

Purpose: public matcher namespace aggregating testtools' assertion matchers.

Important APIs, types, and functions: `__all__` lists basic matchers (`Equals`, `Contains`, `MatchesRegex`, etc.), constant matchers (`Always`, `Never`), data-structure matchers, dict matchers, doctest/exception/filesystem/higher-order/warning matchers, and core protocol classes (`Matcher`, `Mismatch`, `MismatchError`, `MismatchDecorator`). Imports from private modules populate the public namespace.

Control flow: import-time behavior is purely symbol aggregation from implementation modules.

State and persistence: module state consists of imported symbols. No persistent state or I/O.

Dependencies and integration points: consumed by `TestCase.assertThat`, `assertions.assert_that`, and downstream users who import matchers from `testtools.matchers`.

Risks and test signals: public API stability depends on keeping `__all__` and imports synchronized. Test signals are import coverage and matcher-specific tests under `testtools.tests.matchers`.
