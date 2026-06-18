<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/pre-steps/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/pre-steps/action.yml

Purpose: Shared CI setup for RocksDB jobs: diagnostics, optional lld installation, test-output environment, and dependency download mirror variables.

Important APIs/types/functions: dumps soft/hard `ulimit`, runs `apt-get update -y && apt-get install -y lld 2>/dev/null || true`, and writes `GTEST_THROW_ON_FAILURE`, `GTEST_OUTPUT`, `SKIP_FORMAT_BUCK_CHECKS`, `GTEST_COLOR`, `CTEST_OUTPUT_ON_FAILURE`, `CTEST_TEST_TIMEOUT`, plus compression dependency download base URLs to `GITHUB_ENV`.

Control flow: diagnostics run first, package install is best-effort, environment variables are exported for all later steps.

State and persistence behavior: mutates only job environment and package state. Test result XML is directed to `${{ runner.temp }}/test-results/`.

Dependencies and integration points: used by most Linux/macOS CI jobs before make/ctest. Download base variables integrate with third-party dependency build scripts.

Risks: `apt-get` assumes Debian-like environments but errors are ignored. Quoted `GTEST_OUTPUT="xml:..."` writes literal quotes into the env value, which callers must tolerate. Mirror URL drift can break dependency fetches.

Test signals: logs show ulimits; test XML appears in runner temp; CTest failures include output due to exported env.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/pre-steps/action.yml -->
