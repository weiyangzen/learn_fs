## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/run_test.sh

Purpose: In-pod workload script for the GKE machine-type test.

APIs and control flow: Installs OS dependencies, clones gcsfuse at `$GCSFUSE_BRANCH`, validates `.go-version` with a semantic-version regex, installs Go through `perfmetrics/scripts/install_go.sh`, and runs integration tests under `tools/integration_tests/flag_optimizations` with `--mountedDirectory=/data_mnt`, `--testbucket=$BUCKET_NAME`, and a regex selecting implicit-dirs and rename-dir-limit tests.

State and persistence: Mutates the container filesystem, installs Go, and writes test output to pod logs. GCS bucket contents may be touched by integration tests.

Dependencies and risks: Depends on apt, git, build tools, Go version format, GCS bucket access through Workload Identity, and mounted CSI volume at `/data_mnt`.

Test signals: `set -e` makes any install, clone, Go install, or `go test` failure fail the pod.
