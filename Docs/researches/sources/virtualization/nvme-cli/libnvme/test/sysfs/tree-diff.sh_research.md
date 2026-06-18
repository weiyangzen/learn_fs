# File Research: sources/virtualization/nvme-cli/libnvme/test/sysfs/tree-diff.sh

## Role

`tree-diff.sh` is the sysfs topology fixture runner and comparator.

## Behavior

The script takes build directory, tree-dump executable, compressed sysfs input, and expected output. It removes any prior extracted fixture directory, creates a fresh directory, extracts the tarball, and runs `tree-dump` with deterministic environment variables:

- `LIBNVME_SYSFS_PATH` points at the extracted fixture.
- `LIBNVME_HOSTNQN` is a fixed host NQN.
- `LIBNVME_HOSTID` is a fixed host ID.

It captures output into `<test>.out` and compares it to the expected file with `diff -u`.

## Dependencies

- Bash with `-e`.
- `tar`, `diff`.
- `tree-dump` executable.

## Filesystem/Storage Relevance

It is a filesystem-backed fixture harness: libnvme scans an extracted fake sysfs tree instead of the host’s real `/sys`.
