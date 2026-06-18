<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/build-folly/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/build-folly/action.yml

Purpose: Composite GitHub Action that builds Folly and dependencies for RocksDB CI unless a prior `cache-folly` step reported a cache hit.

Important APIs/types/functions: input `cache-hit`; steps `Build folly and dependencies` and `Skip folly build`. The build step strips `/usr/lib/ccache` from `PATH` before running `make build_folly`.

Control flow: if `inputs.cache-hit != 'true'`, it reconstructs a clean PATH and invokes the make target; otherwise it prints a skip message.

State and persistence behavior: creates or updates the Folly getdeps install tree under paths discovered by the surrounding setup/cache actions. It does not itself upload artifacts; cache persistence is owned by `actions/cache`.

Dependencies and integration points: consumed by Folly-enabled PR and nightly jobs after `setup-folly`, `cache-getdeps-downloads`, and `cache-folly`. Depends on repository `folly.mk`, `make build_folly`, bash, and getdeps-prepared sources.

Risks: removing only `/usr/lib/ccache` may miss other ccache wrappers. Cache-hit is a string input, so callers must pass the exact cache output. A stale cache can skip a needed rebuild if the cache key misses an input.

Test signals: CI signal is whether Folly-enabled `make` or CMake jobs proceed past dependency setup and whether logs show either a real build or an intentional cache skip.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/build-folly/action.yml -->
