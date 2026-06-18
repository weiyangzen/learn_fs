# sources/sync-backup/borg/src/borg/testsuite/platform/__init__.py

Purpose: package marker for platform-specific tests.

Important APIs and control flow: no code is defined. The file groups `all_test`, OS-specific ACL/sync tests, and shared platform test helpers under one package.

State and persistence: no state.

Dependencies and integration points: Python package import and pytest discovery.

Risks: removing it can affect relative imports such as `.platform_test`.

Test signals: successful collection of platform test modules.
