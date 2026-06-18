<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/build.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/build.sh

## Purpose
Kokoro presubmit dispatcher that runs expensive performance, integration, package, checkpoint, Orbax, and machine-type tests only when the PR carries opt-in labels.

## Important APIs, Types, And Functions
Defines label constants, `execute_perf_test`, `install_requirements`, and `execute_gke_test`; uses Kokoro env vars and GitHub pull request metadata.

## Control Flow
Fetches PR JSON, checks labels, installs Go and Python dependencies, fetches PR refs, and conditionally runs master/PR fio comparison, integration tests on zonal or non-zonal buckets, package build tests, JAX checkpoints, Orbax GKE benchmark, or machine-type GKE test.

## State And Persistence Behavior
Modifies `.git/config`, checks out branches, mounts/unmounts buckets, writes `result.txt`, installs packages, and creates benchmark artifacts/logs.

## Dependencies
Requires Kokoro artifacts layout, GitHub API, Go, gcsfuse build, fio installer, BigQuery and presubmit requirements, and multiple repo scripts.

## Integration Points
Referenced by `presubmit.cfg`; ties this subset's presubmit scripts and checkpoint script into PR validation.

## Risks And Edge Cases
Label detection uses grep over raw JSON, no API error handling, broad environment assumptions, and branch checkouts happen in-place.

## Test Signals
No unit tests; Kokoro config and label-gated execution are the validation path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/build.sh -->
