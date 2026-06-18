# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/monkey.py

Purpose: monkey-patching utility for tests that need temporary attribute replacement.

Important APIs, types, and functions: `MonkeyPatcher` stores patches and originals, with `add_patch()`, `patch()`, `restore()`, and `run_with_patches()`. Module-level `patch(obj, attribute, value)` applies one patch immediately and returns a restore callable.

Control flow: applying patches records original values or a sentinel for missing attributes, then sets new values. Restore pops originals in reverse order and either restores old values or deletes newly-created attributes. `run_with_patches()` wraps a callable in apply/finally-restore.

State and persistence: mutates live Python object attributes and stores originals in memory until restored. No disk persistence.

Dependencies and integration points: used by `TestCase.patch()` and tests that temporarily replace module globals.

Risks and test signals: double `patch()` before `restore()` stacks originals and can restore to intermediate states; restoring a missing attribute can raise if other code removed it first. Test signals are restoration after exceptions, deletion of newly-added attributes, and cleanup integration with `TestCase.addCleanup`.
