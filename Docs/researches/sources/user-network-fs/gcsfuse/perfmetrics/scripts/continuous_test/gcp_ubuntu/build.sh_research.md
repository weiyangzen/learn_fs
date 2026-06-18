# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/build.sh

## Purpose

Kokoro entrypoint for gcsfuse Ubuntu performance jobs, selecting distributed read, distributed write, local perf tests, or zonal scaffolding based on `BENCHMARK_TYPE`.

## Important APIs, Types, and Functions

Consumes `KOKORO_ARTIFACTS_DIR`, `KOKORO_BUILD_INITIATOR`, `KOKORO_JOB_TYPE`, and `BENCHMARK_TYPE`. Defines `print_duration`, an exit trap, `run_load_test_and_fetch_metrics`, and `run_ls_benchmark`.

## Control Flow

Installs git, enters the Kokoro checkout, identifies branch and commit, then branches by `BENCHMARK_TYPE`. Distributed paths call `gcsfuse-tools/distributed-micro-benchmark/kokoro_run.sh` with read/write flags. `local_tests` builds/installs gcsfuse, installs BigQuery requirements, runs flat and HNS fio/ls benchmarks, and runs HNS rename benchmark. Zonal benchmark currently prints scaffolding.

## State and Persistence Behavior

Installs packages, installs gcsfuse, writes Kokoro logs/artifacts, and invokes downstream scripts that may upload metrics. Changes directories through perfmetrics subtrees.

## Dependencies and Integration Points

Depends on Kokoro layout, Ubuntu apt, git, Docker/package build tooling, pip hashed requirements, gcsfuse-tools, GCS buckets, spreadsheets, and downstream perfmetrics scripts. `continuous.cfg` points to this script.

## Risks and Edge Cases

Scheduler commit selection depends on git history. Hard-coded buckets/spreadsheets/log names require coordinated updates. `pip --require-hashes` requires lock-file sync. Zonal benchmark mode is placeholder-only.

## Test Signals

Printed branch/commit, duration blocks, successful build/install, collected artifacts, successful distributed benchmark exits, and successful local fio/ls/rename completion.
