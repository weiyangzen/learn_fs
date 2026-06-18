# sources/user-network-fs/gcsfuse/tools/integration_tests/run_e2e_tests.sh

## Purpose

`run_e2e_tests.sh` is the main end-to-end integration runner for GCSFuse. It provisions buckets, optionally builds GCSFuse once, installs dependencies, runs integration packages in parallel and non-parallel groups for flat/HNS/zonal/TPC/emulator scenarios, captures logs, and cleans up buckets and build artifacts.

## Important APIs, Types, and Functions

Top-level arguments control installed-package testing, skipping non-essential tests, bucket location, TPC endpoint testing, presubmit mode, zonal bucket mode, and whether the script builds binaries. Arrays define parallel and non-parallel package groups for normal and zonal buckets. Key functions include `build_gcsfuse_once`, `cleanup_gcsfuse_once`, `delete_buckets_listed_in_file`, `upgrade_gcloud_version`, `install_packages`, bucket creation helpers, `run_parallel_tests`, `run_non_parallel_tests`, `print_test_logs`, scenario runners for flat/HNS/zonal/TPC/emulator, and `main`.

## Control Flow

The script validates arguments and bucket-location constraints, adjusts timeout and flags for short/presubmit runs, optionally builds gcsfuse into a temp directory and passes `--gcsfuse_prebuilt_dir`, then chooses zonal-only or normal flat/HNS execution. Flat and HNS paths create separate buckets for parallel and non-parallel package groups. Parallel packages run in background with per-package log files and PID tracking; non-parallel packages run sequentially because they may alter bucket permissions or shared state. On failure, logs are printed. The exit trap cleans built binaries and deletes all buckets listed in the generated bucket file.

## State and Persistence Behavior

The script creates temporary bucket-name and log-list files, multiple GCS buckets, optional HNS/zonal bucket resources, temporary build directories, and per-package logs under `/tmp`. It installs or upgrades system packages and modifies `PATH`/`CLOUDSDK_PYTHON`. Cleanup is trap-based and best-effort for buckets.

## Dependencies and Integration Points

It depends on Bash, `gcloud`, Go, Python, apt packages, project-specific perfmetrics install scripts, `tools/build_gcsfuse`, and every package under `tools/integration_tests`. It integrates with bucket projects `gcs-fuse-test-ml` and `gcs-fuse-test`, HNS and zonal bucket creation, TPC endpoint tests, and emulator tests.

## Risks and Edge Cases

The script has several shell robustness risks: early use of `$4` before checking argument count, a stray quote in `upgrade_gcloud_version`, global variables shared across functions, and extensive unquoted expansions. Bucket cleanup is critical because it creates real cloud resources. Parallel package execution can mask shared-resource conflicts if a package is incorrectly classified. Hard-coded projects and locations require CI-specific permissions.

## Test Signals

Primary signals are package-level pass/fail logs, final exit code, and printed logs on failure. Strong success means flat/HNS or zonal bucket groups complete, all created buckets are removed by the trap, and optional built binaries are cleaned.
