<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/benchmark-linux.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/benchmark-linux.yml

Purpose: Manually triggered benchmark workflow for RocksDB Linux benchmark runs.

Important APIs/types/functions: workflow name `facebook/rocksdb/benchmark-linux`; trigger `workflow_dispatch`; job `benchmark-linux` uses checkout, `build-for-benchmarks`, `perform-benchmarks`, and `post-benchmarks`.

Control flow: only runs for `github.repository_owner == 'facebook'`, builds release binaries, runs benchmark script, uploads and posts benchmark results.

State and persistence behavior: creates build outputs, benchmark DB/temp data, benchmark result artifacts, and optional external visualization documents.

Dependencies and integration points: composes the three benchmark actions in this subset. Depends on GitHub runner temp storage and benchmark tooling in the repository.

Risks: schedule is commented out as temporarily disabled, so benchmarks require manual dispatch. Uses `ubuntu-latest` with a FIXME to return to self-hosted, so performance comparability is limited.

Test signals: successful manual workflow with `benchmark-results` artifact and benchmark report TSV.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/benchmark-linux.yml -->
