# File Research: sources/virtualization/nvme-cli/libnvme/test/nbft/meson.build

## Role

`test/nbft/meson.build` defines NBFT parser tests over stored ACPI NBFT binary fixtures.

## Behavior

It builds `nbft-dump` from `nbft-dump.c`, configures helper scripts for diffing and regenerating expected output, and adds a `nbft-diffs` run target.

When `diff` is available, each good table fixture is tested by piping `nbft-dump` output into a unified diff against its stored expected output. Bad fixtures are registered as expected failures, using `expected_fail` for Meson >= 1.11.0 and `should_fail` for older Meson.

## Fixtures

Good tables include IPv4/IPv6, DHCP/static, discovery, multipath, Dell PowerEdge examples, half IPv4/IPv6 discovery, and empty-table cases. Bad tables include an old-spec table and random noise.

## Dependencies

- Meson.
- `diff` for golden-output comparisons.
- libnvme NBFT parser via `nbft-dump`.

## Filesystem/Storage Relevance

NBFT describes boot-time NVMe-oF discovery and connection configuration. These tests validate libnvme’s ability to parse that storage boot metadata.
