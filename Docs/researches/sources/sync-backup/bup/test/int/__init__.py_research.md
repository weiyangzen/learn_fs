<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/__init__.py -->
# sources/sync-backup/bup/test/int/__init__.py

Purpose: marks `test/int` as a Python package for integration tests. It defines no APIs, functions, classes, control flow, or state. Persistence behavior is limited to the file's presence in the source tree, which can influence import/package discovery. Dependencies are Python's package import rules and the test runner's collection behavior. Risks are low; deleting or renaming it could change relative import behavior for tests or helper modules on older tooling. Test signal is implicit: pytest and local imports collect and run integration tests without package import errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/__init__.py -->
