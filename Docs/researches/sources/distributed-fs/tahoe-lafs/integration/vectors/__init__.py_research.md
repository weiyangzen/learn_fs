# sources/distributed-fs/tahoe-lafs/integration/vectors/__init__.py

## Purpose
Package facade for vector-related constants, data types, serialization helpers, loaded capabilities, and maximum share metadata.

## Important APIs, Types, and Functions
Defines `__all__` and re-exports `DATA_PATH`, `CURRENT_VERSION`, `Case`, `Sample`, `SeedParam`, `encode_bytes`, `save_capabilities`, `capabilities`, and `MAX_SHARES` from sibling modules.

## Control Flow
Import-time work is limited to importing names from `.vectors` and `.parameters`. Any YAML loading side effects belong to `.vectors`, not this facade.

## State and Persistence
No local persistence. It exposes persisted vector state through `capabilities` and `DATA_PATH`.

## Dependencies and Integration Points
Used by `test_vectors.py` as `from . import vectors`, allowing tests to access a curated package-level API without reaching into implementation modules.

## Risks
Facade drift is the main risk: adding new vector model names without updating `__all__` or imports can make package-level consumers fail.

## Test Signals
Indirect signal is successful import and access to vector constants/classes by `test_vectors.py`.
