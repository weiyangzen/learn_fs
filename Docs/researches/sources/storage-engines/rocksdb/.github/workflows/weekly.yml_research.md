<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/weekly.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/weekly.yml

Purpose: Weekly long-running RocksDB Valgrind CI workflow.

Important APIs/types/functions: scheduled at `0 9 * * 0` plus manual dispatch; job `build-linux-valgrind` runs with `timeout-minutes: 840`, 16-core Ubuntu runner, RocksDB Ubuntu 22.1 container, shared pre-steps, `make V=1 -j20 valgrind_test`, and post-steps.

Control flow: owner-gated weekly job checks out the repo, applies common environment, runs Valgrind tests, then uploads artifacts.

State and persistence behavior: creates Valgrind/test outputs and post-step artifacts. No durable repo state.

Dependencies and integration points: complements PR/nightly workflows with expensive memory-check coverage.

Risks: very long timeout and Valgrind overhead can consume runner capacity. Container/toolchain drift can affect reports. Failures may be delayed until weekly cadence.

Test signals: weekly Valgrind pass/fail and uploaded logs for memory diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/weekly.yml -->
