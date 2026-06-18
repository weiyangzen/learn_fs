# sources/storage-engines/wiredtiger/test/compatibility/common/compatibility_version.py

Purpose: Defines a comparable branch/version object for compatibility scenario generation.

Important APIs/types/functions: `WTVersion.__init__` recognizes `this`, `develop`, and exact `mongodb-X.Y` branch names. Rich comparison methods order versions by group and numeric major/minor, with `this` higher than `develop`, and `develop` higher than numbered branches. `__bool__`, `__eq__`, `__hash__`, and `__str__` support filtering, set membership, and display.

Control flow: construction parses and records validity; comparisons are pure value comparisons. String equality is supported in `__eq__` to simplify membership checks.

State and persistence: instances persist branch name, validity, group, major, and minor in memory only.

Dependencies/integration: used by `compatibility_config`, scenario generation, and tests that define version boundaries such as FLCS or chunk-cache deprecation.

Risks and test signals: `this` is marked valid only briefly before the `else` tied to `develop` can invalidate it, so the intended `this > develop > mongodb-*` behavior should be tested carefully. Invalid versions are falsey and can be filtered away without an explicit diagnostic.
