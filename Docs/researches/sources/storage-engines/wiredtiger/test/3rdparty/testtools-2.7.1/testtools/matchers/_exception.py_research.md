# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/_exception.py

Purpose: matchers for exception tuples and callables expected to raise.

Important APIs, types, and functions: `MatchesException(exception, value_re=None)` validates `sys.exc_info()`-style tuples against an exception type/tuple or instance and optional message matcher/regex. `Raises(exception_matcher=None)` calls a nullary callable and matches the resulting exception. `raises(exception)` is a convenience factory for `Raises(MatchesException(exception))`.

Control flow: `MatchesException` rejects non-tuples, checks class compatibility, compares args for expected exception instances, and optionally matches exception value. `Raises.match()` calls the matchee, reports a mismatch if it returns, catches all exceptions, and re-raises non-`Exception` subclasses such as `KeyboardInterrupt` unless explicitly matched.

State and persistence: matcher instances store expected exception criteria. No persistence.

Dependencies and integration points: depends on `sys`, `MatchesRegex`, deprecated alias `AfterPreproccessing`, and core matcher classes. Used by `TestCase.assertRaises` and `ExpectedException`.

Risks and test signals: string `value_re` is matched with `re.match` through `MatchesRegex`, not substring search. Catch-all exception handling is deliberate but delicate for system-exiting exceptions. Tests cover type, instance args, regex messages, returned-callable mismatch, and propagation behavior.
