# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/errors.h

Read status: complete, 65 lines.

This header defines the `Err` and `Warn` enums used by `sam` diagnostics. The enum order matches the message arrays in `error.c`.

Errors include open/create/I/O failures, parser errors, address/search/regexp errors, command execution failures, dirty-file conditions, temp overflow, append-only writes, plumbing failures, and buffer-load failures. Warnings include duplicate names, missing files, date conflicts, NUL elision, pwd failure, missing final newline, and bad exit status.

Filesystem relevance: enumerates file and buffer failure conditions used across the editor.
