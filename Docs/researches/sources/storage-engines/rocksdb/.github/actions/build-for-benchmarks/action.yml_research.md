<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/build-for-benchmarks/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/build-for-benchmarks/action.yml

Purpose: Composite action for preparing a Linux release build before benchmark execution.

Important APIs/types/functions: invokes local `pre-steps` and runs `make V=1 J=8 -j8 release`.

Control flow: setup/environment defaults are applied first, then a release build is compiled.

State and persistence behavior: produces RocksDB release build outputs in the checkout workspace. Benchmark data is produced later by `perform-benchmarks`.

Dependencies and integration points: used by `benchmark-linux.yml`; depends on GNU make, compiler toolchain, and the shared `pre-steps` action.

Risks: fixed `-j8` assumes runner capacity. It does not set up ccache, so benchmark build time can be high. Failures in `pre-steps` or release compilation block benchmark runs.

Test signals: successful benchmark workflow reaches `perform-benchmarks`; build logs show a completed `release` target.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/build-for-benchmarks/action.yml -->
