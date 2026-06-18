# sources/object-store/daos/src/vos/storage_estimator/common/tests/pytest.ini

## Purpose
Pytest configuration for storage-estimator tests.

## Important APIs, Types, And Functions
Defines markers `ut`, `sx`, `rp3gx`, and `ec16p2` for data-structure unit tests and object-class-specific estimator scenarios.

## Control Flow
Pytest reads this file during collection to register marker names and avoid unknown-marker warnings.

## State And Persistence
No state or persistence.

## Dependencies And Integration
Used by `storage_estimator.sh`, which invokes pytest separately for each marker.

## Risks
Marker names must match decorators in `storage_estimator_test.py` and shell invocations. New object-class scenarios need marker additions.

## Test Signals
Running `python -m pytest -m ut/sx/rp3gx/ec16p2` exercises the configured markers.
