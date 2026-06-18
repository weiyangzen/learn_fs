# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj_lex.h

## Purpose
Defines the small lexer interface used by selected kernel modules to parse on-disk system files through kobj file buffers.

## Main Interfaces
- Character classification macros:
  - `isunary()`
  - `iswhite()`
  - `isnewline()`
  - `isalphanum()`
  - `isnamechar()`
- `token_t`: token enum covering punctuation, whitespace, EOF, strings, numeric values, and names.
- Debug-only `tokennames[]`.
- Parser helpers:
  - `kobj_get_string()`
  - `kobj_free_string()`
  - `kobj_getvalue()`
  - `kobj_file_err()`
  - `kobj_lex()`
  - `kobj_find_eol()`

## Dependencies And Relationships
Includes `sys/ctype.h` and uses `struct _buf` from kobj file handling. It is intended for a few kernel modules, not broad general kernel parsing.

## Research Notes
String helper ownership is explicit: strings returned through `kobj_get_string()` must be released with `kobj_free_string()`. `kobj_file_err()` includes file context and prints through kernel error reporting.
