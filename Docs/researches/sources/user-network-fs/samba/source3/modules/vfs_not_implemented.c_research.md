# sources/user-network-fs/samba/source3/modules/vfs_not_implemented.c

## Purpose
`vfs_not_implemented.c` is the negative/default implementation table for Samba's VFS layer. It supplies exported fallback functions for every VFS hook that has no real implementation in a module, returning `ENOSYS`, `NT_STATUS_NOT_IMPLEMENTED`, `NT_STATUS_NOT_SUPPORTED`, or other SMB-compatible "not available" statuses. Its registration also asserts that the table covers every VFS function pointer, making it a coverage guard for VFS interface evolution.

## Important APIs, Types, And Functions
- Exports many `_PUBLIC_` functions named `vfs_not_implemented_*` spanning connection, disk, directory, file, DFS, snapshot, ACL, xattr, AIO, FSCTL, byte-range lock, durable handle, compression, and copy-offload hooks.
- Async placeholders such as `vfs_not_implemented_offload_read_send`, `vfs_not_implemented_offload_write_send`, `vfs_not_implemented_get_dos_attributes_send`, and `vfs_not_implemented_getxattrat_send` allocate `tevent_req` objects and complete them immediately with an NTSTATUS or Unix error.
- `struct vfs_fn_pointers vfs_not_implemented_fns` binds every hook to the matching fallback.
- `vfs_not_implemented_init()` calls `smb_vfs_assert_all_fns()` before `smb_register_vfs(..., "vfs_not_implemented", ...)`.

## Control Flow
Most synchronous hooks are single-exit stubs: set `errno`, zero outputs where necessary, and return a failure sentinel. NTSTATUS-oriented hooks return Samba protocol statuses directly. Async hooks create a request, mark it failed via `tevent_req_nterror()` or `tevent_req_error()`, post it to the event loop, and have receive functions propagate the stored status/error before `tevent_req_received()`.

## State And Persistence
The module owns no persistent external state. It may initialize output buffers to safe empty values, such as zero disk-space counters or zeroed `struct file_id`, and async helper structs hold only transient request state.

## Dependencies And Integration Points
It depends on Samba VFS structs, `tevent`, and NTSTATUS utilities. Other modules explicitly reference its functions for hooks they intentionally do not implement, for example `offline` and `posix_eadb` use the not-implemented async DOS/xattr hooks. The all-functions assertion makes this file sensitive to changes in `struct vfs_fn_pointers`.

## Risks
- Interface drift is the main risk: a new VFS hook must be added here or `smb_vfs_assert_all_fns()` should fail.
- Return semantics must match the hook family. A wrong `errno`, status, or async completion style can change upper-layer fallback behavior.
- Stubbed async receive functions must set `vfs_aio_state->error` consistently so callers do not treat an unsupported operation as transient I/O.

## Test Signals
- Build-time registration should pass `smb_vfs_assert_all_fns()`.
- Loading `vfs_not_implemented` should register successfully.
- Unsupported VFS calls should surface expected SMB errors, for example `NT_STATUS_NOT_IMPLEMENTED`, `NT_STATUS_NOT_SUPPORTED`, `NT_STATUS_INVALID_DEVICE_REQUEST`, or `ENOSYS`.
- Async stub callers should observe immediate completion with the correct error.
