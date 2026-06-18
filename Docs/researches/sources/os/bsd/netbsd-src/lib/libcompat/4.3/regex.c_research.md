# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.3/regex.c

## Purpose
Implements old `re_comp()`/`re_exec()` compatibility APIs in terms of the historical `regexp` interface.

## Behavior
`re_comp()` frees any previous compiled expression and error string, compiles a new expression with `regcomp()`, and returns an error string on failure. `re_exec()` runs `regexec()` against the stored expression and returns `-1` if compilation/execution signaled an error. `regerror()` records the error string for these wrappers.

## Dependencies
Depends on `<regexp.h>`, `<re_comp.h>`, `regcomp()`, `regexec()`, and global compatibility state.

## Risks And Notes
The implementation is not thread-safe because compiled regexp and error state are static globals. `re_exec()` assumes a prior successful `re_comp()` initialized `re_regexp`.
