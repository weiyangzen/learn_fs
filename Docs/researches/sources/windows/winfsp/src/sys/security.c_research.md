# File Research: sources/windows/winfsp/src/sys/security.c

## Purpose

`security.c` implements `IRP_MJ_QUERY_SECURITY` and `IRP_MJ_SET_SECURITY` for WinFsp filesystem volume devices. It combines file-node security descriptor caching with fallback user-mode filesystem requests.

## Main Contents

- Query path:
  - `FspFsvolQuerySecurity`
  - `FspFsvolQuerySecurityComplete`
  - `FspFsvolQuerySecurityRequestFini`
- Set path:
  - `FspFsvolSetSecurity`
  - `FspFsvolSetSecurityComplete`
  - `FspFsvolSetSecurityRequestFini`
- Dispatch entries:
  - `FspQuerySecurity`
  - `FspSetSecurity`

## Query Flow

`FspFsvolQuerySecurity`:

1. Validates the file node and file descriptor.
2. Acquires the file node main resource shared.
3. If a cached security descriptor exists, releases the node and answers directly with `FspQuerySecurityDescriptorInfo`.
4. Otherwise acquires the paging I/O/full lock path.
5. Buffers the caller output buffer for write access.
6. Creates a `FspFsctlTransactQuerySecurityKind` request.
7. Stores file-node ownership in request context and posts to IOQ.

`FspFsvolQuerySecurityComplete`:

- Propagates user-mode failure status.
- Validates the returned relative security descriptor bounds and format.
- Releases file-node ownership after capturing the security change number.
- Tries to reacquire the file-node main resource exclusively.
- If reacquisition fails, retries completion through `FspIopRetryCompleteIrp`.
- Attempts to cache the descriptor if the file-node security change number still matches.
- Answers the original query from cached security if possible, otherwise from the response buffer.
- Sets `IoStatus.Information` to the resulting descriptor length.

## Set Flow

`FspFsvolSetSecurity`:

- Validates file node and descriptor relationship.
- Determines whether the input security descriptor is self-relative.
- Computes the self-relative size.
- Acquires the file node full resource exclusively.
- Creates a `FspFsctlTransactSetSecurityKind` request with extra buffer space.
- Copies or converts the descriptor into the request buffer.
- Sets file-node ownership and posts to IOQ.

`FspFsvolSetSecurityComplete`:

- Propagates user-mode failure status.
- If user mode returns a valid relative security descriptor, updates the cached descriptor.
- Otherwise invalidates the cached security descriptor.
- Marks the file descriptor as having set security and metadata.
- Emits a security change notification.
- Releases request ownership.
- Completes with zero information.

## Integration

The file depends on:

- file-node security cache helpers,
- `FspQuerySecurityDescriptorInfo` from `util.c`,
- `FspIopCreateRequestEx`,
- request-finalizer ownership cleanup,
- IOQ retry completion for lock contention during completion.

## Notable Details

- The query path can complete entirely from cached metadata without contacting user mode.
- Returned security descriptors are required to be relative and valid before caching.
- The set path assumes the kernel has captured a valid security descriptor; disabled code documents the validation point.
