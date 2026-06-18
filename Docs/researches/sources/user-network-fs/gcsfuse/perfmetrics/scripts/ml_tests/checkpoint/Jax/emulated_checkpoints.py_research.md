<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/emulated_checkpoints.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/emulated_checkpoints.py

## Purpose
Creates a synthetic JAX/Flax training state and writes repeated checkpoints to a supplied directory, exercising GCSFuse checkpoint write behavior.

## Important APIs, Types, And Functions
`SimpleModel` Flax module, `train_step`, and CLI arguments `--checkpoint_dir` and `--num_train_steps`.

## Control Flow
Initializes random sample data and a deep dense model, builds an Adam train state, performs one gradient update, then loops over training steps and saves a checkpoint every 200 steps with prefix `checkpoint_` and `keep=100`.

## State And Persistence Behavior
Writes checkpoint files to the supplied directory, which the wrapper mounts on flat, HNS, and zonal buckets.

## Dependencies
Uses JAX, Flax, Optax, and `flax.training.checkpoints` with dependencies pinned in the sibling requirements file.

## Integration Points
Called by `run_checkpoints.sh` after mounting target buckets with streaming writes enabled.

## Risks And Edge Cases
The model is very large for a mock workload, checkpoint writes can be expensive, and only one real train step occurs before repeated saves. Failure handling is left to the wrapper process.

## Test Signals
No direct unit test in this subset; integration signal is the shell wrapper running it against multiple bucket types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/emulated_checkpoints.py -->
