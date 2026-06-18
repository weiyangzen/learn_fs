
# sources/sync-backup/kopia/tests/perf_benchmark/perf-benchmark-setup.sh

## Purpose
Prepares a Linux benchmark host by installing tools and formatting/mounting a data device for Kopia performance benchmarks.

## Important APIs, Types, And Functions
Shell script with `set -e`; installs `fio` and `python3-pip`, installs Python `psrecord`, formats `/dev/nvme0n1` as ext4, mounts it at `/mnt/data`, and changes ownership to `$USER`.

## Control Flow
Commands run sequentially and abort on first failure. There is no argument parsing or safety confirmation.

## State And Persistence Behavior
Destructively formats `/dev/nvme0n1`, creates `/mnt/data`, mounts it, and changes ownership.

## Dependencies And Integration Points
Depends on Debian/Ubuntu-style `apt`, `pip3`, root/sudo privileges, and a benchmark environment where `/dev/nvme0n1` is safe to wipe.

## Risks And Edge Cases
Very high destructive risk if run on the wrong machine. The script assumes device name and mount point, does not check existing mounts, and uses system Python package installation.

## Test Signals
Operational setup artifact rather than a test; it supports reproducible benchmark environments.
