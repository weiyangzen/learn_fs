# sources/user-network-fs/samba/source3/lib/netapi/file.c

## Purpose

`file.c` implements the `NetFile*` libnetapi operations for open-file administration through the SRVSVC RPC interface. It was read as a complete 283-line file. The module lets callers close an open server-side file handle, fetch file metadata, and enumerate open files while returning Windows-compatible `FILE_INFO_2` and `FILE_INFO_3` buffers.

## Important APIs, Types, and Functions

Public internal entry points are `NetFileClose_r/_l`, `NetFileGetInfo_r/_l`, and `NetFileEnum_r/_l`. The important mapper is `map_srvsvc_FileInfo_to_FILE_INFO_buffer()`, which converts `union srvsvc_NetFileInfo` level 2 or 3 results into `FILE_INFO_2`/`FILE_INFO_3` arrays using `ADD_TO_ARRAY`. Remote calls use `libnetapi_get_binding_handle(..., &ndr_table_srvsvc, ...)`, `dcerpc_srvsvc_NetFileClose`, `dcerpc_srvsvc_NetFileGetInfo`, and `dcerpc_srvsvc_NetFileEnum`.

## Control Flow

Each `_r` function validates output pointers and levels, obtains an SRVSVC binding handle, calls the matching DCERPC operation, translates `NTSTATUS` failures to `WERROR`, and maps RPC output into caller-owned talloc buffers rooted at the libnetapi context. `NetFileEnum_r` initializes a level-specific `srvsvc_NetFileInfoCtr`, calls enumeration with `base_path`, `user_name`, `prefmaxlen`, and `resume_handle`, accepts `WERR_MORE_DATA`, then iterates returned records and appends mapped entries.

## State and Persistence Behavior

The module owns no durable state. `NetFileClose_r` mutates remote server state by closing an open file ID. Get/enum paths allocate transient API buffers under `ctx`; callers release them through `NetApiBufferFree` or context teardown. Resume state is maintained externally through the caller-provided resume handle.

## Dependencies and Integration Points

The file depends on generated `libnetapi` and SRVSVC NDR headers, `netapi_private` binding helpers, talloc memory, `WERROR`/`NTSTATUS` conversion helpers, and the public wrappers in `libnetapi.c`. Local `_l` functions use `LIBNETAPI_REDIRECT_TO_LOCALHOST`, so the same remote implementation path is reused for local-server requests.

## Risks and Edge Cases

Only information levels 2 and 3 are supported; invalid levels return `WERR_INVALID_LEVEL`. `NetFileEnum_r` iterates `info_ctr.ctr.ctr2->count` even for level 3 after assigning `ctr3`, which depends on compatible union layout or is a potential null/wrong-counter risk. It also overwrites `total_entries` with `num_entries`, losing the server-reported total after enumeration. String duplication failures are checked, but partial arrays may already be attached to `ctx` on errors.

## Test Signals

Useful tests include SRVSVC integration tests for levels 2 and 3, invalid-level and null-buffer checks, `WERR_MORE_DATA` resume behavior, close-by-fileid behavior, and memory ownership checks that returned path/user strings survive after the RPC frame is freed.
