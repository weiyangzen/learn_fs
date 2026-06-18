<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/nightly-candidate.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/nightly-candidate.yml

Purpose: Manual holding workflow for nightly jobs that are currently broken or not ready for the main nightly schedule.

Important APIs/types/functions: workflow name currently matches `facebook/rocksdb/nightly`; trigger `workflow_dispatch`; job `build-linux-arm-test-full` installs gflags and runs `make V=1 J=4 -j4 check` on `arm64large`.

Control flow: only runs for repository owner `facebook`; checkout, pre-steps, install gflags, full check, post-steps.

State and persistence behavior: produces build/test outputs and artifacts through `post-steps`; no persistent repo state.

Dependencies and integration points: related to `nightly.yml` but separated for failing/broken candidates.

Risks: workflow name duplicates the main nightly name, which can confuse workflow_run triggers and UI. Requires an `arm64large` self-hosted label that may be unavailable.

Test signals: manual dispatch success indicates the ARM full test candidate may be ready for promotion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/nightly-candidate.yml -->
