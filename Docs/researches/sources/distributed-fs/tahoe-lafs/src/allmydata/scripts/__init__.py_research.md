# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/__init__.py

## Purpose
Marks `allmydata.scripts` as a Python package. The file is intentionally empty and exposes no runtime API of its own.

## APIs, Types, And Control Flow
There are no functions, classes, constants, imports, or executable statements. Package import behavior is the only API surface: modules such as `runner`, `cli`, `create_node`, and command-specific implementations are imported by fully qualified `allmydata.scripts.*` names.

## State, Persistence, And Integration
No state is persisted. Integration is structural only, enabling Tahoe-LAFS command modules to share a package namespace.

## Risks And Test Signals
The practical risk is accidental addition of import-time side effects, which would affect CLI startup. Current test signal is indirect: any CLI test importing `allmydata.scripts` or a submodule validates that the package marker exists and remains harmless.
