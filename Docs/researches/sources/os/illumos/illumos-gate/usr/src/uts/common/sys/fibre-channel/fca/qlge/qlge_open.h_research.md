# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_open.h

## Role

`qlge_open.h` provides build-time defaults for the illumos `qlge` Ethernet driver.

## Definitions

The file conditionally defines:
- `VERSIONSTR` as `100721-v1.07`.
- `QL_DEBUG` as `0x0`.
- `__func__` as `"qlge"` if the compiler/environment has not defined `__func__`.

## Integration Notes

The values are guarded with `#ifndef`, allowing build-time overrides. The file has no structs or function prototypes and is included by `qlge.h`.
