# File Research: sources/os/linux/linux/fs/dlm/rcom.c

## Role

`rcom.c` implements DLM recovery communication messages. RCOMs coordinate recovery status barriers, directory name transfer, resource master lookup, and lock-copy rebuilding.

## Message Creation

`create_rcom()` allocates a midcomms reliable message. `create_rcom_stateless()` allocates a lowcomms message directly for early/status exchanges that must remain compatible with version detection and their own retry handling.

`_create_rcom()` fills the DLM RCOM header, type, lockspace id, sender nodeid, length, and recovery sequence.

## Status and Config

`dlm_rcom_status()` sends a status request and waits synchronously for a reply using `ls_rcom_seq` and `LSFL_RCOM_WAIT`. It retries on timeout and validates remote config values such as LVB length and lockspace flags.

`receive_rcom_status()` replies with current recovery status and optional slot data when requested.

`receive_sync_reply()` copies the reply into `ls_recover_buf` only if the reply id matches the current wait sequence.

## Directory and Master Recovery

`dlm_rcom_names()` requests resource names from a peer during directory rebuild. `receive_rcom_names()` replies with names selected by `dlm_copy_master_names()`.

`dlm_send_rcom_lookup()` asks a directory node for the new master of a resource. `receive_rcom_lookup()` performs `dlm_master_lookup()` and replies with the selected nodeid. Lookup replies are handed to `dlm_recover_master_reply()`.

## Lock Recovery

`pack_rcom_lock()` serializes an LKB and optional LVB into `struct rcom_lock`.

`dlm_send_rcom_lock()` sends local process-copy lock state to the new master. `receive_rcom_lock()` calls `dlm_recover_master_copy()` and replies with remid/result data. Lock replies are processed by `dlm_recover_process_copy()`.

## Lockspace Not Ready

`dlm_send_ls_not_ready()` sends a status reply with `-ESRCH` for a lockspace that is not ready or not present. The requester treats this as a remote lockspace with zero status during early recovery.

## Receive Filtering

`dlm_receive_rcom()` gates messages by recovery stop state, recovery sequence, and stage:
- name/lookup/lock messages are ignored before node status is reached
- lookup/lock messages are ignored before directory recovery is reached
- replies with stale sequence ids are ignored
- short lock recovery messages are rejected

## Important Behaviors and Invariants

- RCOM status messages are part of version detection and use stateless lowcomms paths.
- `ls_recover_buf` is the single synchronous reply buffer for recovery waits.
- Recovery stage bits prevent future-stage messages from being processed too early.
- Reply sequence checks avoid applying stale recovery replies after a new recovery generation begins.

## Research Notes

Read completely. This file is recovery’s network protocol implementation and is tightly coupled to `recover.c`, `recoverd.c`, `member.c`, and `dir.c`.
