# File Research: sources/virtualization/nvme-cli/libnvme/test/test-fabrics.c

## Role

`test-fabrics.c` unit-tests static helper functions from `src/nvme/fabrics.c` by including that source file directly after redefining `static` away.

## Behavior

The file uses a small `CHECK` macro and `test_rc` accumulator to print pass/fail status. It tests:

- `strchomp()` trailing-space removal.
- `hostid_from_hostnqn()` UUID extraction.
- Argument-building helpers for boolean, hex, integer, integer-or-minus-one, and string arguments.
- `inet4_pton()` IPv4 parsing and error handling.
- `inet_pton_with_scope()` IPv4/IPv6 parsing, scoped IPv6, null service, and port overflow.
- `traddr_is_hostname()` classification, especially ensuring scoped IPv6 like `fe80::1%lo` is not misclassified as a hostname.
- `unescape_uri()` percent decoding, explicit length truncation, invalid percent sequences, and truncated percent sequences.

A real libnvme context is created because some helper error paths log through `libnvme_msg()`.

## Dependencies

- Direct inclusion of `../src/nvme/fabrics.c`.
- Public and internal libnvme symbols.
- Network address parsing APIs.
- Built with `-fgnu89-inline` in Meson to avoid inline linkage problems caused by redefining `static`.

## Filesystem/Storage Relevance

This validates NVMe-oF connection argument construction and address classification, which affects how storage targets are discovered and connected.
