# File Research: sources/os/plan9/9front/sys/src/cmd/sam/errors.h

`errors.h` defines sam's `Err` and `Warn` enums. The enum order is significant because `error.c` indexes static message tables by these values.

`Err` includes open/create/menu/modified/I/O/write-sequence errors, command-character errors, delimiter and operand errors, address/search/regex/substitution/range/order errors, command execution and pipe errors, dirty-file exit checks, file-search ambiguity, temporary-file overflow, append-only writes, plumbing failures, and buffer-load failures.

`Warn` covers duplicate names/files, missing files, possible stale writes, NUL elision, current-directory lookup failure, missing final newline, and non-empty shell command exit status.
