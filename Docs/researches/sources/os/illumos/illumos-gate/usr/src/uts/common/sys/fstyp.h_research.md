# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fstyp.h

## Role

`fstyp.h` defines the legacy `sysfs(2)` filesystem-type query ABI.

## Key Interfaces and Data

- `FSTYPSZ` defaults to 16, the maximum filesystem identifier size.
- `GETFSIND` maps a filesystem identifier to a filesystem type index.
- `GETFSTYP` maps an index back to an identifier.
- `GETNFSTYP` returns the number of configured filesystem types.
- Declares `int sysfs(int, ...)` outside `_KERNEL`.

## Dependencies and Use

The header has no heavy includes and is suitable for userland. It preserves historical AT&T/SVR4 API shape.

## Research Notes

This is a stable, small compatibility header; the key risk for consumers is fixed-size identifier handling via `FSTYPSZ`.
