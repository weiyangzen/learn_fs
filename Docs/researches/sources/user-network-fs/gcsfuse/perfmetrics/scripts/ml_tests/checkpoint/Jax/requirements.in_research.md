<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/requirements.in

## Purpose
Pinned JAX/Flax checkpoint dependency set.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Pins JAX, jaxlib, flax, optax, orbax-checkpoint/tensorstore-related packages, numpy/scipy, protobuf, and rich UI dependencies.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Pins JAX, jaxlib, flax, optax, orbax-checkpoint/tensorstore-related packages, numpy/scipy, protobuf, and rich UI dependencies.

## Integration Points
Installed in the checkpoint wrapper venv with hashes before running `emulated_checkpoints.py`.

## Risks And Edge Cases
Tightly pinned versions improve reproducibility but require compatible Python and platform wheels.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/requirements.in -->
