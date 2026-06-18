# sources/user-network-fs/samba/source3/modules/vfs_error_inject.c

## Purpose
`vfs_error_inject.c` injects configured Unix errors or panic behavior into selected VFS paths for fault testing.

## Important APIs, Types, And Functions
`unix_error_map_array` maps `ESTALE`, `EBADF`, `EINTR`, `EACCES`, and `EROFS`. `inject_unix_error()` reads `error_inject:<function>`. Wrappers cover `chdir`, `pwrite`, `openat`, `unlinkat`, and `durable_reconnect`. Durable reconnect decodes and can mutate `vfs_default_durable_cookie`.

## Control Flow
Simple wrappers set errno and fail when configured, otherwise delegate. `openat_create` fires only for new `O_CREAT` targets and generic open injection skips pathref directory opens. `unlinkat` injects only if the parent is not owned by the current user. Durable reconnect can increment `stat_info.st_ex_nlink` in the default durable cookie before delegation.

## State And Persistence
There is no persistent state. Configuration is read at call time. Durable cookie mutation affects only that reconnect request.

## Dependencies And Integration Points
The module depends on loadparm, path helpers, parent pathname resolution, current uid helpers, NDR durable-cookie definitions, and lower VFS hooks.

## Risks
Only a small errno set is supported. Unknown strings log and delegate, which can mask misconfigured tests. Durable reconnect is coupled to the default cookie format. `panic` is intentionally destructive.

## Test Signals
Test each errno on each hook, unknown strings, panic in controlled runs, create-only open errors, pathref bypass, unlink owner bypass, durable cookie mutation, and unset delegation.
