# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tags.py

Purpose: small tag context object for tracking currently active test result tags.

Important APIs, types, and functions: `TagContext(parent=None)` stores a parent and a set of current tags. `get_current_tags()` returns a copy. `change_tags(new_tags, gone_tags)` adds and removes tags and returns the current set.

Control flow: a child context copies parent tags on construction. Result objects push a new `TagContext` at test start and pop it at test stop, while `tags()` events mutate the current context.

State and persistence: in-memory set state only. No persistence.

Dependencies and integration points: used by `testtools.testresult.doubles.ExtendedTestResult` and real stream/result implementations to model nested tag scopes.

Risks and test signals: tag names are not validated; callers must pass sets or set-like iterables. Test signals are parent inheritance, add/remove behavior, and isolation through returned copies.
