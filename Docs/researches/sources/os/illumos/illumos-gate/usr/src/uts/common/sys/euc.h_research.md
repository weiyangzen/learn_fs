# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/euc.h

## Role

`euc.h` defines EUC character-set width helpers and the `eucwidth_t` structure used by older multibyte locale and line-discipline code.

## Definitions

- Defines EUC shift bytes `SS2` and `SS3`.
- Defines byte classification macros `ISASCII()`, `NOTASCII()`, `ISSET2()`, `ISSET3()`, and `ISPRINT()`.
- Defines `eucwidth_t` with EUC byte widths for codesets 1-3, screen widths for codesets 1-3, process-code width, and a `_multibyte` flag.

## Contract Notes

The header is guarded so `NOTASCII` and `_EUCWIDTH_T` are not redefined if already supplied. `ISPRINT()` depends on an `eucwidth_t` value and `isprint()`.
