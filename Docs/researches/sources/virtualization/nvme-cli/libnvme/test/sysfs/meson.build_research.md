# File Research: sources/virtualization/nvme-cli/libnvme/test/sysfs/meson.build

## Role

`test/sysfs/meson.build` defines sysfs topology golden-output tests.

## Behavior

If `diff` is found, it builds `test-tree-dump` from `tree-dump.c`, declares two sysfs fixture names (`tree-pcie` and `tree-apple-nvme`), locates `tree-diff.sh`, and registers one test per fixture.

Each test passes the build directory, dumper path, compressed sysfs fixture tarball, and expected output file to `tree-diff.sh`.

## Dependencies

- Meson.
- `diff`.
- `tree-diff.sh`.
- libnvme dependency.

## Filesystem/Storage Relevance

This validates libnvme’s sysfs topology scanning against captured NVMe device trees.
