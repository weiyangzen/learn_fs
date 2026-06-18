# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/_impl.py

Purpose: core matcher protocol, mismatch representation, assertion error, and mismatch decoration base.

Important APIs, types, and functions: `Matcher` defines abstract `match()` and `__str__()`. `Mismatch` stores an optional description and details dict. `MismatchError` subclasses `AssertionError` and formats failure text, optionally verbose. `MismatchDecorator` forwards `describe()` and `get_details()` to an underlying mismatch.

Control flow: concrete matchers return `None` or `Mismatch`; assertion helpers raise `MismatchError`. `MismatchError.__str__()` calls `mismatch.describe()` and includes matchee/matcher metadata in verbose mode. Details are exposed for `TestCase` to attach to results.

State and persistence: mismatch objects hold descriptions/details; errors hold matchee/matcher/mismatch. No persistence.

Dependencies and integration points: depends on `testtools.compat.text_repr`. It is used by every matcher module and by `TestCase.assertThat`/`assert_that`.

Risks and test signals: `Matcher` is a protocol base, not an enforced ABC. `Mismatch` without description must override `describe()` or raise `NotImplementedError`. Test signals are detail propagation, verbose formatting, and decorator forwarding.
