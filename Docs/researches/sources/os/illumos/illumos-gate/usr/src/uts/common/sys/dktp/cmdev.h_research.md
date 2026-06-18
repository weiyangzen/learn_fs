# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmdev.h

## Scope

Complete file read, 40 lines. This header provides SCSI device address access macros for DKTP common device code.

## Public Surface

It defines:

- `CMDEV_TARG(devp)` as `(devp)->sd_address.a_target`
- `CMDEV_LUN(devp)` as `(devp)->sd_address.a_lun`

## Behavior And Integration

There is no executable behavior. The macros abstract target and LUN extraction from a `struct scsi_device`-like pointer used by DKTP direct access disk code.

## Dependencies And Invariants

The `devp` argument must refer to an object with `sd_address.a_target` and `sd_address.a_lun` fields. No type checking or null checking is performed.

## Risks

Because these are raw lvalue macros, passing an incompatible pointer produces compile-time or runtime breakage depending on context. They also evaluate `devp` once, so side effects are limited but still undesirable.
