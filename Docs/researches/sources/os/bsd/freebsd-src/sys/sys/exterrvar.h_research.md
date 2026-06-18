# File Research: sources/os/bsd/freebsd-src/sys/sys/exterrvar.h

## Purpose
Defines kernel and userland interfaces for FreeBSD extended error reporting.

## Main Interfaces
- Includes `_exterr.h`, `_uexterror.h`, and `exterr_cat.h`.
- Constants:
  - `UEXTERROR_MAXLEN`
  - `UEXTERROR_VER`
  - `EXTERRCTL_ENABLE`, `DISABLE`, `UD`
  - `EXTERRCTLF_FORCE`
- Kernel requires `EXTERR_CATEGORY` before inclusion.
- Kernel macros:
  - `EXTERROR(...)`
  - `EXTERROR_KE(...)`
  - helper selectors for zero, one, or two parameters
- Kernel APIs:
  - `exterr_clear`
  - `exterr_db_print`
  - `exterr_set_from`
  - `exterr_set`
  - `exterr_to_ue`
  - `ktrexterr`
- Userland API: `exterrctl`.

## Dependencies And Integration
Kernel macros capture error code, category, optional string, two uintptr parameters, and source line. `EXTERR_STRINGS` controls whether messages are retained.

## Risk Notes
Callers must define the correct category before inclusion. Macro argument dispatch is sensitive to call shape, and source-line capture is part of diagnostic value.
