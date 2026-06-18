# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/_warnings.py

Purpose: matchers for verifying warnings emitted by callables.

Important APIs, types, and functions: `WarningMessage()` builds a `MatchesStructure` matcher for `warnings.WarningMessage` attributes: category, message, filename, lineno, and line. `Warnings(warnings_matcher=None)` records warnings emitted by a callable. `IsDeprecated(message)` requires exactly one `DeprecationWarning` whose message matches the supplied matcher.

Control flow: `Warnings.match()` enters `warnings.catch_warnings(record=True)`, forces `simplefilter('always')`, calls the matchee, and either matches the captured warnings list or reports no warnings. `WarningMessage` composes annotated attribute matchers and stringifies warning messages before matching.

State and persistence: temporarily changes warnings filters within the context manager, then restores them. No persistent state.

Dependencies and integration points: depends on Python `warnings`, basic/constant/data-structure/higher-order matchers, and core `Mismatch`. Used in tests for deprecation behavior.

Risks and test signals: callable exceptions propagate and prevent warning matching. There is a typo in the annotation text `"filname"`, affecting diagnostics only. Test signals include no-warning mismatch, deprecation warning matching, message matcher behavior, and filter restoration.
