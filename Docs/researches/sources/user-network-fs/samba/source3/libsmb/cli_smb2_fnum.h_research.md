# sources/user-network-fs/samba/source3/libsmb/cli_smb2_fnum.h

## Purpose
`cli_smb2_fnum.h` declares the source3 SMB2/SMB3 fnum compatibility API implemented by `cli_smb2_fnum.c`. It lets callers that were written around SMB1-style `uint16_t` fnums perform SMB2 operations without directly handling SMB2 persistent/volatile FIDs, create contexts, or lower-level `smb2cli_*` request objects.

## Important APIs, Types, And Functions
The only concrete public type in this header is `struct cli_smb2_create_flags`, with `batch_oplock` and `exclusive_oplock` bitfields. The header forward-declares `smbXcli_conn`, `smbXcli_session`, `cli_state`, `file_info`, and `symlink_reparse_struct`, keeping the public surface narrow while relying on other Samba headers for full definitions of `DATA_BLOB`, `NTSTATUS`, `SMB_NTQUOTA_STRUCT`, `SMB_NTQUOTA_LIST`, `smb2_create_blobs`, `smb_create_returns`, and notify structures.

The create/open API is `cli_smb2_create_fnum_send/recv()` and synchronous `cli_smb2_create_fnum()`. It accepts SMB2 create parameters, optional input create blobs, and returns an fnum plus optional create returns, output blobs, and symlink information. `cli_smb2_fnum_is_posix()` exposes whether an fnum originated from a POSIX-context open.

Handle operations include close, delete-on-close, generic query-info and set-info by fnum, read/write/writeall, splice/copychunk, truncate, notify, and FSCTL. Path operations include mkdir, rmdir, unlink, list, qpathinfo, setpathinfo, set attributes, query filesystem size/attributes/volume data, maximum access, rename, and EA get/set helpers. Quota functions operate on a quota fnum and marshal user or filesystem quota data.

The header consistently exposes async send/recv pairs for operations that can naturally fit tevent workflows, plus synchronous convenience wrappers for legacy callers. Synchronous functions all take `struct cli_state *cli` and typically return `NTSTATUS`; async send functions take `TALLOC_CTX *mem_ctx`, `struct tevent_context *ev`, and `struct cli_state *cli`.

## Control Flow
The header encodes a layered control-flow contract. Callers can either use send/recv pairs and drive them through a tevent loop, or call synchronous wrappers that internally create and poll a tevent request. For path operations that have no direct SMB2 path-level primitive, the implementation opens a temporary fnum, performs a handle-level operation, and closes it before returning.

Create, list, notify, fsctl, read, write, writeall, splice, and POSIX filesystem info are explicitly asynchronous in the interface. Directory listing has a special receive contract: `cli_smb2_list_recv()` can return one `file_info`, report `NT_STATUS_RETRY` while another query-directory request is outstanding, or terminate with no-more-files/error semantics.

## State And Persistence
The header does not declare state storage, but its API implies fnum lifetime state inside `cli_state`. Any fnum returned by create or opened internally by path helpers maps to an SMB2 server handle until closed. Functions that mutate remote persistence include create, mkdir, rmdir, unlink, set-info, set attributes, rename, EA writes, quota writes, copychunk, truncate, and delete-on-close.

Memory ownership is part of the API contract. Receive functions use caller-provided memory contexts for output blobs, symlink data, `file_info` arrays, EA arrays, shadow copy names, notify changes, and FSCTL output. Callers must keep the request alive long enough for direct receive buffers documented by the implementation, especially read buffers returned from `cli_smb2_read_recv()`.

## Dependencies And Integration Points
This header is included by source3 client code that dispatches SMB2 behavior from generic `libsmb` APIs. It depends on Samba-wide NTSTATUS, tevent, talloc, SMB2 create context, quota, EA, file-info, and notify type definitions being visible through surrounding includes. It integrates with the lower-level `smb2cli_*` layer indirectly through the implementation, and with legacy SMB1-facing caller code by preserving fnum-shaped handles and historical behavior.

## Risks And Test Signals
The broad API surface means signature drift can break many consumers. Build tests should include source3 clients, `libsmbclient`, quota tools, and SMB2 POSIX feature paths. Async contract tests should verify each send/recv pair handles posted errors, cancellation where supported, memory-context transfer, and request cleanup.

The header exposes several nuanced contracts that need tests: POSIX fnum detection, directory-list retry iteration, read buffer lifetime, set attribute SMB1-compatible semantics, quota-fnum usage, notify timeout behavior, and FSCTL output ownership. Because many synchronous wrappers reject operation while another async request is in flight, mixed async/sync caller tests should assert `NT_STATUS_INVALID_PARAMETER` rather than deadlock or protocol corruption.
