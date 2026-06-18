<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/nightly.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/nightly.yml

Purpose: Scheduled and manual nightly RocksDB CI covering long-running, platform-specific, Folly, Windows, ARM, examples, and fuzz build lanes.

Important APIs/types/functions: triggers daily at `0 9 * * *` and `workflow_dispatch`; jobs include format compatibility, non-shm Linux check, clang21 ASAN/UBSAN with Folly, CMake/release Folly builds, Windows AVX2, ARM full/crash tests, examples, fuzzers, and Folly-lite CMake.

Control flow: each job is guarded to `github.repository_owner == 'facebook'`; most jobs checkout, run shared pre-steps and specialized dependency setup, execute make/CMake/ctest commands, then upload post-step artifacts.

State and persistence behavior: produces build directories, test temp data, crash-test files, swapfile on ARM crash job, and artifacts. No commits or durable repo changes.

Dependencies and integration points: shares actions from this subset (`pre-steps`, `setup-folly`, `cache-folly`, `build-folly`, `windows-build-steps`, `post-steps`) and exercises repository scripts such as `check_format_compatible.sh`, fuzz Makefiles, and crash tests.

Risks: long-running nightly jobs depend on self-hosted labels, container images, external package managers, and large `/dev/shm`/swap resources. One Folly ASAN job manually disables ccache wrappers, which is fragile. ARM crash job mutates system swap and shm.

Test signals: daily green nightly workflow, uploaded artifacts/logs, and coverage of paths too expensive for PR CI.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/nightly.yml -->
