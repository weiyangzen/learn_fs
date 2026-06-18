# sources/sync-backup/borg/src/borg/testsuite/crypto/__init__.py

Purpose: package marker for crypto tests under `borg.testsuite.crypto`.

Important APIs and control flow: the file defines no imports, helpers, fixtures, or runtime logic. Its function is to make sibling modules importable as a package.

State and persistence: no state is read or written.

Dependencies and integration points: integration is Python package discovery for tests that use relative imports from `...crypto` and `..`.

Risks: the risk is structural rather than behavioral; removing it can change package import semantics in older tooling or direct test invocation modes.

Test signals: import collection of the crypto test package is the only signal.
