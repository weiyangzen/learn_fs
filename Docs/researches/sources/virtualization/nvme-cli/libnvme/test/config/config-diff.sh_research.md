# File Research: sources/virtualization/nvme-cli/libnvme/test/config/config-diff.sh

## Purpose
Test wrapper for config JSON/sysfs fixture diff tests.

## Behavior
Parses `--sysfs-tar` and `--config-json`, unpacks a sysfs tarball into the build directory when provided, sets `LIBNVME_SYSFS_PATH`, `LIBNVME_HOSTNQN`, and `LIBNVME_HOSTID`, runs the requested test binary with the config JSON path, captures output, and compares it to the expected `.out` file with `diff -u`.

## Relevance
Provides deterministic config/topology tests without depending on the host machine’s real NVMe sysfs state.
