# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gserror.h

## Role

`gserror.h` defines Ghostscript error-return logging macros.

## API

Declares:

- `gs_log_error(int, const char *, int)`

In non-DEBUG builds, `gs_log_error(err, file, line)` is macro-reduced to just `err`.

Defines:

- `gs_note_error(err)` as `gs_log_error(err, __FILE__, __LINE__)`
- `return_error(err)` as `return gs_note_error(err)`

## Dependencies

Uses compiler `__FILE__` and `__LINE__`.

## Integration Notes

This header lets code annotate error returns with source location in DEBUG builds while keeping release builds cheap.

## Risks

`return_error` directly returns from the current function. It must only be used in functions whose return type and error-code convention match Ghostscript integer status codes.
