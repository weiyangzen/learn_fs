# sources/object-store/daos/src/vos/storage_estimator/common/tests/__init__.py

## Purpose
Package initializer for storage-estimator common tests.

## Important APIs, Types, And Functions
Exports `util` through `__all__`, making local test helpers importable as `storage_estimator.common.tests.util` or relative `.util`.

## Control Flow
No runtime control flow beyond package import.

## State And Persistence
No state or persistence.

## Dependencies And Integration
Supports `storage_estimator_test.py`, which imports `FileGenerator` from `.util`.

## Risks
If additional test helper modules are added, wildcard exports will not include them until this list is updated.

## Test Signals
Validated indirectly by pytest collecting and importing the test package.
