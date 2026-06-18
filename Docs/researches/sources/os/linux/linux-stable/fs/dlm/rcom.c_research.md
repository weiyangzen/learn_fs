# File Research: sources/os/linux/linux-stable/fs/dlm/rcom.c

## Purpose
`rcom.c` implements DLM recovery communication messages: status, directory-name transfer, master lookup, lock-copy transfer, and replies.

## Message Creation
- `create_rcom()` creates recovery messages through midcomms, using reliable 3.2 handling when available.
- `create_rcom_stateless()` sends directly through lowcomms for status messages used by version detection and recovery polling.
- `_create_rcom()` fills the common `struct dlm_rcom` header.

## Status and Config
`dlm_rcom_status()` sends status requests and waits synchronously for replies through `ls_recover_buf`. It retries on timeout and verifies remote config compatibility with `check_rcom_config()`.

Status replies include:
- recovery status bits
- LVB length
- lockspace flags
- local slot/generation data
- optional serialized slot map when requested

`dlm_send_ls_not_ready()` sends an `-ESRCH` status reply when a lockspace does not yet exist or is not ready.

## Directory Recovery
`dlm_rcom_names()` requests chunks of master resource names from another node. `receive_rcom_names()` calls `dlm_copy_master_names()` to fill the reply with directory-rebuild records.

## Master Lookup Recovery
`dlm_send_rcom_lookup()` sends a resource-name lookup to a directory node. `receive_rcom_lookup()` calls `dlm_master_lookup(..., DLM_LU_RECOVER_MASTER, ...)` and replies with the selected master node. `receive_rcom_lookup_reply()` passes replies to `dlm_recover_master_reply()`.

## Lock Recovery
`dlm_send_rcom_lock()` serializes a process-copy lock into `struct rcom_lock`, including modes, ids, flags, AST availability, resource name, and optional LVB bytes.

`receive_rcom_lock()` calls `dlm_recover_master_copy()` to rebuild master-copy state, then replies with remid/result. `DLM_RCOM_LOCK_REPLY` is handled by `dlm_recover_process_copy()`.

## Receive Filtering
`dlm_receive_rcom()` filters recovery messages by:
- current stop state
- recovery sequence
- recovery phase status bits
- message type
- minimum length for lock-copy messages

It ignores messages that arrive too early for the local recovery phase, logging limited diagnostics.

## Risks and Notes
Synchronous reply state uses `ls_rcom_seq`, `LSFL_RCOM_WAIT`, `LSFL_RCOM_READY`, and `ls_recover_buf`. Correctness depends on sequence checks and phase gating so stale recovery replies cannot mutate current recovery state.
