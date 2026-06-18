# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdint.h

## Role

System implementation backing for ISO C99 `<stdint.h>`.

## Key Contents

Includes integer type, limit, and constant headers: `<sys/int_types.h>`, `<sys/int_limits.h>`, and `<sys/int_const.h>`.

## Design Notes

The header is intentionally only a composition layer over illumos integer definitions and does not define integer types directly.
