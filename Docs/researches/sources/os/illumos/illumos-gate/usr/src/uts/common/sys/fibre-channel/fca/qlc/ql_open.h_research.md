# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_open.h

## Role

`ql_open.h` provides build-time default identity/version settings for the illumos `qlc` Fibre Channel adapter driver.

## Definitions

The file conditionally defines:
- `QL_VERSION` as `151216-3.07`.
- `QL_NAME` as `qlc`.
- `QL_DEBUG` as `0x0`.
- `OS_MAJ` as `11`.

## Integration Notes

The values are guarded with `#ifndef`, allowing the build system or including source to override them. The header has no function prototypes or data structures.
