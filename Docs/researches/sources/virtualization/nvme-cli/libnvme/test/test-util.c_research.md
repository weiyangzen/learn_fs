# File Research: sources/virtualization/nvme-cli/libnvme/test/test-util.c

## Role

`test-util.c` tests public and private utility helpers from libnvme’s utility layer.

## Behavior

It validates `libnvme_get_version()` for project version, git version, and invalid version type. It tests `libnvme_ipaddrs_eq()` across equal IPv4, compressed/equivalent IPv6, null pairs, IPv4-mapped IPv6 equivalence, unequal IPv4/IPv6, invalid strings, and null/non-null cases.

It exhaustively checks `nvme_id_ns_flbas_to_lbaf_inuse()` for `flbas` values `0x00` through `0x7f`, comparing against the expected LBA format index mapping.

The test prints aligned pass/fail status and exits failure if any group fails.

## Dependencies

- Public `<libnvme.h>`.
- Internal `<nvme/private.h>`.
- Network database headers.

## Filesystem/Storage Relevance

The LBA format helper is directly storage-relevant because it interprets namespace format state. IP comparison supports NVMe-oF address handling.
