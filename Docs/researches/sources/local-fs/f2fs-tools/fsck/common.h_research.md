# File Research: sources/local-fs/f2fs-tools/fsck/common.h

## Purpose
Small quota/common utility header providing logging macros and compiler attribute compatibility.

## Key contents
- Header guard: `__QUOTA_COMMON_H__`.
- Undefines `DEBUG_QUOTA` by default.
- Defines `__attribute__(x)` away for older/non-GNU compilers under strict conditions.
- Provides:
  - `log_err(format, arg...)`: prints file, line, function, and error message to stderr.
  - `log_debug(format, arg...)`: enabled only if `DEBUG_QUOTA` is defined; otherwise compiles to nothing.

## Dependencies
Uses standard `fprintf`, `stderr`, and `__FILE__`, `__LINE__`, `__func__` assumptions from including translation units.

## Research notes
Despite living in `fsck/`, this header is quota-oriented support code. It does not carry F2FS-specific structures.
