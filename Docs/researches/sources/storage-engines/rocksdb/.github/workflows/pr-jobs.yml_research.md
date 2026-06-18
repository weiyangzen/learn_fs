<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/pr-jobs.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/pr-jobs.yml

Purpose: Main RocksDB PR/push CI workflow aggregating fast checks and broad build/test coverage across Linux, macOS, Windows, Java, sanitizers, Folly, ARM, and formatting.

Important APIs/types/functions: top-level `ONLY_JOB` override; `config` job exports it. Jobs include `check-format-and-targets`, core Linux `make check`, CMake MinGW, Folly make/CMake, benchmark CMake shards, encrypted env no compression, release builds, clang/gcc no-test builds, unity/header checks, mini crash tests, ASAN/UBSAN/TSAN shards, alternate namespace static build, macOS make/CMake/Java variants, Windows VS2022 matrix, Java/PMD, and ARM subset build. Uses many composite actions from this subset.

Control flow: jobs run on push/pull_request but are owner-gated to `facebook` unless `ONLY_JOB` is set. Matrix jobs shard tests by CTest or selected suite lists. Shared setup/post actions wrap most jobs; ccache setup/teardown surrounds compiler-heavy lanes.

State and persistence behavior: creates build directories, ccache directories, test temp outputs, PMD/Maven artifacts, failure logs, core dumps, and uploaded GitHub artifacts. No repository commits are made.

Dependencies and integration points: central integration point for local actions (`pre-steps`, `setup-ccache`, `teardown-ccache`, `post-steps`, Folly/cache actions, macOS installers, Windows build action), repository Make/CMake targets, container images, self-hosted runner labels, GitHub artifacts, and downstream AI review `workflow_run` triggers.

Risks: a single workflow contains many independent lanes, so syntax errors can block all PR signal. Owner gating prevents fork runner hangs but reduces fork-local validation. Many jobs depend on specific labels/images/tool versions. `ONLY_JOB` is powerful but requires editing workflow env. High parallelism and large artifacts can stress runners.

Test signals: required PR checks, matrix shard results, uploaded test artifacts, ccache stats, and downstream workflow_run consumers such as AI review wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/pr-jobs.yml -->
