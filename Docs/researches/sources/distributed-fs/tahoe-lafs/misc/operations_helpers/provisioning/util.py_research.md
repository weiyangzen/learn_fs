# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/util.py

## Purpose

This utility module provides a path helper for files adjacent to the provisioning modules.

## Important APIs, Types, and Functions

`sibling(filename)` returns `os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)`.

## Control Flow

There is no control flow beyond the helper function.

## State, Dependencies, Integration, Risks, and Tests

No state is persisted. Dependency is `os.path`. Integration is template loading in `provisioning.py` and `web_reliability.py`. Risks are minimal; it assumes `__file__` is meaningful. Tests should verify it returns absolute paths in the module directory for known template filenames.
