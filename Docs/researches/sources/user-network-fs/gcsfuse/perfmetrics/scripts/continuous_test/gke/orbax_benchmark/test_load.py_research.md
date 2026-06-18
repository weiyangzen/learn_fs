## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/test_load.py

Purpose: In-pod CLI for loading and resaving Orbax checkpoints while measuring restore time.

APIs and control flow: Provides `set_no_of_jax_cpu`, `load_ckpt`, `save_ckpt`, Click group `cli`, and commands `load_test` and `resave`. `load_ckpt` reads Orbax metadata, rewrites array sharding metadata for CPU/TPU backends when needed, converts metadata to shape/dtype structs, restores with `StandardCheckpointer`, logs restored types, and returns elapsed time plus restored data. `load_test` repeats restore and prints per-loop and average timings.

State and persistence: Mutates `XLA_FLAGS` and JAX config, may clear JAX caches, loads checkpoint data into memory, and `resave` writes a checkpoint to the output path.

Dependencies and risks: Requires absl, click, etils, jax, numpy, and orbax. Sharding rewrite assumes leading dimension divisibility for some arrays. `RESTORE_CONCURRENT_GB` can drive high resource use.

Test signals: Printed loop timings and average elapsed time are consumed indirectly by pod logs.
