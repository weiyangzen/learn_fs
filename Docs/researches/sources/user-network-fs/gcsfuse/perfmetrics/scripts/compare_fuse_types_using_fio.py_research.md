# sources/user-network-fs/gcsfuse/perfmetrics/scripts/compare_fuse_types_using_fio.py

## Purpose

Runs a fio workload against two FUSE-based filesystems mounted on the same GCS bucket and writes parsed metrics to `out/output.txt`.

## Important APIs, Types, and Functions

Defines `GCSFUSE_REPO`, `GCSFUSE_FLAGS`, `_install_gcsfuse`, `_install_gcsfuse_source`, `_remove_gcsfuse`, `_install_fuse`, `_remove_fuse`, `_run_fio_test`, `_gcsfuse_fio_test`, `_fuse_fio_test`, `_fuse_test`, and `main`. Uses `fio.fio_metrics.FioMetrics` and `absl.app.run`.

## Control Flow

Parses two filesystem names, versions/repo URLs, mount flags, a fio jobfile, and a GCS bucket. Creates `out`, labels filesystem 1, installs/mounts it, runs fio and parses `output.json`, cleans up, then repeats for filesystem 2.

## State and Persistence Behavior

Installs/removes packages, clones/removes repos, creates/removes a `gcs` mountpoint, mounts/unmounts FUSE filesystems, temporarily writes `output.json`, and appends durable comparison output to `out/output.txt`.

## Dependencies and Integration Points

Requires fio, fusermount, sudo/dpkg/apt for gcsfuse releases, git, Go, GCS credentials, local `fio` Python package, and absl. Integrates with gcsfuse releases/source and arbitrary Go FUSE repos.

## Risks and Edge Cases

Uses unquoted f-string shell commands through `os.system` and does not inspect exit codes. Flags/paths/repo URLs with shell metacharacters are risky. Generic FUSE support assumes a Go project accepting `go run . flags gs://bucket mountpoint`. Concurrent runs conflict on `gcs`, `output.json`, and `out`.

## Test Signals

Mock `os.system` and `FioMetrics.get_metrics` to assert command ordering. Operational signals are successful mount/fio/unmount, parsed metrics in `out/output.txt`, and no stale mount/package/clone artifacts.
