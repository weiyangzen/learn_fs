# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/error.c

## Purpose
`error.c` adapts com_err reporting to ss subsystem and current-request context.

## Important APIs, Types, and Functions
Public functions are `ss_name()`, `ss_error()`, and compatibility `ss_perror()`.

## Control Flow
`ss_name()` allocates either the subsystem name or `subsystem (request)` when a command is active. `ss_error()` builds that prefix, forwards formatted output to `com_err_va()`, and frees the prefix. `ss_perror()` calls `ss_error()` with a `%s` format.

## State, Persistence, Dependencies, Risks, and Test Signals
State is read from `ss_data.current_request` and subsystem name. Dependencies include `com_err` and `ss_internal.h`. Risks include allocation failure handling gaps in the request-name path and global table validity. Test signals are correctly prefixed errors for unknown commands and active command failures.
