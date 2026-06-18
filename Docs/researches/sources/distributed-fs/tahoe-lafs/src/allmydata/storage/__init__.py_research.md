# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/__init__.py

## Purpose
Marks `allmydata.storage` as a Python package. The file is intentionally empty.

## Important APIs, Types, and Functions
No APIs, classes, functions, or module constants are defined.

## Control Flow
No runtime control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Enables imports of sibling modules such as `allmydata.storage.immutable`, `http_client`, `http_server`, `crawler`, `expirer`, and `lease`.

## Risks and Edge Cases
Because it exports nothing, package-level imports must import concrete submodules explicitly. Empty-file behavior is stable.

## Test Signals
Covered indirectly by every test importing `allmydata.storage.*`.
