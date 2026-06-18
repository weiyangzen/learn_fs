# File Research: sources/local-fs/xfsprogs/repair/err_protos.h

## Role

`err_protos.h` declares the shared diagnostic and fatal error functions used throughout repair code.

## API

- `do_abort`: fatal internal error, marked `noreturn` and printf-format checked.
- `do_error`: fatal system or repair error, marked `noreturn` and printf-format checked.
- `do_warn`: nonfatal warning.
- `do_log`: progress/log output.

## Importance

The printf format attributes give compile-time validation for the many translated diagnostic strings throughout repair. The distinction between abort/error/warn/log is central to xfs_repair’s behavior in no-modify versus modifying modes.
