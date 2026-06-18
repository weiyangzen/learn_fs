# File Research: sources/os/linux/linux/fs/lockd/svcproc.c

## Purpose
`svcproc.c` implements the NLM version 1 and version 3 server procedures. It decodes already-parsed legacy `nlm_args`, performs common host/file lookup, invokes shared lock/share/resource engines, supports async callback-style procedures, and exports the `svc_version` definitions for NLMv1 and NLMv3.

## Main Responsibilities
- Maps internal lockd statuses to protocol-safe v1/v3 statuses through `cast_status()`.
- Performs common argument retrieval in `nlmsvc_retrieve_args()`: verifies callbacks are installed, looks up host, optionally starts NSM monitoring, opens the target file, and initializes `struct file_lock`.
- Implements synchronous TEST, LOCK, CANCEL, UNLOCK, GRANTED, SHARE, UNSHARE, NM_LOCK, FREE_ALL, SM_NOTIFY, and GRANTED_RES handlers.
- Implements `_MSG` async forms by computing a result and sending an async callback response before returning.
- Defines the 24-entry legacy procedure table shared by v1 and v3, with v1 exposing procedures 0 through 16.
- Defines XDR storage requirements and per-CPU call counters for v1/v3.

## Key Procedure Behavior
- TEST calls `nlmsvc_testlock()` and returns conflict details in `nlm_res.lock`.
- LOCK calls `nlmsvc_lock()` with `block` and `reclaim` arguments.
- CANCEL and UNLOCK reject during grace period, then call `nlmsvc_cancel_blocked()` or `nlmsvc_unlock()`.
- GRANTED hands server grant callbacks to the NLM client side via `nlmclnt_grant()`.
- SHARE and UNSHARE invoke DOS share reservation helpers.
- NM_LOCK clears the monitor flag then reuses the LOCK path.
- FREE_ALL retrieves the host without opening a file and frees all host resources.
- SM_NOTIFY accepts only privileged statd callbacks and calls `nlm_host_rebooted()`.
- GRANTED_RES forwards callback status to `nlmsvc_grant_reply()`.

## Integration Points
- Uses legacy XDR functions from `xdr.c`/`xdr.h`.
- Uses `svclock.c` for POSIX lock operations and blocked lock handling.
- Uses `svcshare.c` for share reservations.
- Uses `svcsubs.c` for file lookup and host resource traversal.
- Uses SUNRPC async reply helpers through `nlm_async_reply()`.

## Concurrency and Lifetime Notes
- Host, file, and lockowner references are acquired in `nlmsvc_retrieve_args()` and released by each procedure after the shared operation.
- Async callback allocation uses `nlm_alloc_call()`; the release callback decrements the call refcount and releases its host.
- The common retrieval path sets `FL_POSIX`, `flc_file`, `flc_pid`, `fl_lmops`, and lockowner private data before handing the lock to VFS operations.

## Risks and Edge Cases
- If `nlmsvc_ops` is absent, most real procedures fail with denied-no-locks because file handle callbacks are unavailable.
- Status casting is intentionally lossy for older protocols, especially when v4-specific statuses or internal statuses must map to v1/v3 status space.
- v1 procedure exposure is narrower than v3, but both share the same table definition.
