<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/pr-jobs-candidate.yml -->
# Research: sources/storage-engines/rocksdb/.github/workflows/pr-jobs-candidate.yml

Purpose: Manual staging workflow for PR jobs that are failing or not ready for the main PR workflow.

Important APIs/types/functions: workflow_dispatch only; jobs `build-linux-arm` and `build-linux-arm-cmake-no_test_run` on `arm64large`; uses checkout, `pre-steps`, `install-gflags`, make/CMake commands, Java environment setup, and `post-steps`.

Control flow: owner-guarded jobs run ARM make or CMake build variants manually.

State and persistence behavior: creates build outputs and artifacts only.

Dependencies and integration points: mirrors jobs that may later move into `pr-jobs.yml`; depends on ARM self-hosted runners and JDK path `/usr/lib/jvm/java-8-openjdk-arm64`.

Risks: candidate jobs are explicitly broken or unstable. Hardcoded runner labels and Java paths can block execution.

Test signals: manual green candidate runs justify promotion into regular PR CI.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/workflows/pr-jobs-candidate.yml -->
