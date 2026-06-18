# sources/user-network-fs/samba/source3/modules/vfs_time_audit.c

## Purpose

`vfs_time_audit.c` is an instrumentation VFS module that measures elapsed time for Samba VFS calls and logs a warning when an operation exceeds a configurable threshold. It is designed to diagnose slow storage, filesystem, network, or lower VFS-module behavior without changing operation semantics. It registers as `time_audit`.

## Important APIs, Types, And Functions

The module has one global setting, `audit_timeout`, loaded from `time_audit:timeout` in milliseconds and stored as seconds. Logging helpers are `smb_time_audit_log_msg()`, `smb_time_audit_log()`, `smb_time_audit_log_fsp()`, `smb_time_audit_log_at()`, `smb_time_audit_log_fname()`, and `smb_time_audit_log_smb_fname()`.

Most wrappers follow a standard pattern: capture `clock_gettime_mono()` before and after `SMB_VFS_NEXT_*`, compute `nsec_time_diff() * 1.0e-9`, and log if above threshold. Async operations maintain small state structs that capture FSP or path context and use `vfs_aio_state.duration` or send/receive monotonic timestamps in recv callbacks. The function table is broad and ends with `smb_vfs_assert_all_fns(&vfs_time_audit_fns, "time_audit")`, which asserts that every VFS operation has an audit wrapper.

## Control Flow

The wrappers delegate to the next VFS module and preserve return values. Path-aware operations sometimes build a full filename before timing so log messages include useful context. Create/open/close, directory operations, stat variants, quota, DFS, snapshot, read/write/sendfile/recvfile, rename, fsync, allocation, lock, lease, ACL, xattr, compression, copy offload, durable handle, and DOS attribute paths are all covered.

Async wrappers such as pread, pwrite, fsync, get DOS attributes, getxattrat, offload read, and offload write create a parent request, call the next async send function, store results in a state struct in the callback, and log from recv based on the lower layer's reported duration or send-to-recv elapsed time.

## State And Persistence

There is no filesystem persistence. Runtime state is limited to the global `audit_timeout` and per-async-request talloc state. The persistent side effect is log output at `DEBUG(0)` warning level when calls exceed the threshold.

## Dependencies And Integration Points

The module depends on Samba VFS macro APIs, monotonic time helpers, `tevent` async request helpers, NT status tevent helpers, Samba pathname and FSP structures, and debug logging. It is built as `vfs_time_audit` in `source3/modules/wscript_build` and listed among default shared modules in `source3/wscript`. Because it asserts all VFS functions, it is sensitive to VFS interface changes and acts as coverage pressure for new hooks.

## Risks And Edge Cases

Instrumentation overhead is small but nonzero on every VFS call, including very hot read/write/stat paths. Some logging helpers dereference contextual structures such as `dir_fsp`, `smb_fname`, `fsp->conn`, or `fsp->fsp_name`; most common null cases are handled, but not every helper is equally defensive. If logging itself blocks or allocates heavily during storage stalls, the module can add noise. Because the timeout is global static state, per-share configuration changes after module initialization are not represented. Wrappers must preserve `errno` on failure; most do, and `fallocate` explicitly saves it, but this is a recurring regression risk.

## Test Signals

Tests should load the module with a very low timeout and verify warning logs for representative sync and async VFS calls. ABI tests should confirm `smb_vfs_assert_all_fns()` passes after VFS interface changes. Failure-path tests should check `errno`/NTSTATUS preservation for operations like open, unlink, fallocate, xattr reads, and async receives.
