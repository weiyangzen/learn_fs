# File Research: sources/os/linux/linux/fs/dlm/dir.c

## Role

`dir.c` implements the DLM resource directory. The directory maps a resource name hash to the node responsible for answering "who is the master of this resource?" It also implements directory reconstruction during recovery by exchanging resource names between members.

## Directory Node Selection

`dlm_hash2nodeid(struct dlm_ls *ls, uint32_t hash)` chooses the directory node:

- Single-node lockspaces always use `dlm_our_nodeid()`.
- Multi-node lockspaces use the upper 16 bits of the resource hash, modulo `ls_total_weight`, as an index into `ls_node_array`.

The comment states that low hash bits are reserved for RSB hash-bucket distribution, while high bits choose the directory node. `dlm_dir_nodeid(struct dlm_rsb *r)` simply returns the cached `res_dir_nodeid`.

`dlm_recover_dir_nodeid()` recomputes `res_dir_nodeid` for each RSB in a recovery root list after membership changes.

## Directory Recovery

`dlm_recover_directory(struct dlm_ls *ls, uint64_t seq)` rebuilds local directory records by asking every other current member for the names it masters and for which this node is directory owner.

Main flow:

1. If `dlm_no_directory(ls)` is set, skip directory exchange and mark directory recovery complete.
2. Allocate `last_name` as the cursor for chunked remote name dumps.
3. For each remote member, repeatedly call `dlm_rcom_names()` with the last name received.
4. Parse returned `namelen/name` records from `ls_recover_buf->rc_buf`.
5. Interpret `namelen == 0` as end of this buffer chunk and `namelen == 0xFFFF` as end of that node's full dump.
6. For every resource name, call `dlm_master_lookup(..., DLM_LU_RECOVER_DIR, ...)`.
7. Count names received, new records added, and unexpected mismatched master records.
8. Set recovery status `DLM_RS_DIR`.

The parser bounds-checks each name against both the remaining buffer and `DLM_RESNAME_MAXLEN`. It returns `-EINVAL` on malformed recovery data and `-EINTR` if recovery is stopped.

## Master Name Dump Context

Remote nodes serve directory recovery requests using `dlm_copy_master_names()`. Because a node may need multiple response messages to dump all matching resource names, this file maintains a per-requesting-node `struct dlm_dir_dump` context on `ls_dir_dump_list`.

`struct dlm_dir_dump` tracks:

- Initial recovery sequence and requesting nodeid.
- The last `res_masters_list` pointer sent.
- Count of resources and messages sent for logging.

The context is protected by `ls_dir_dump_lock`; resource master list iteration is protected by `ls_masters_lock`.

## Dump Lifecycle

- `init_dir_dump()` creates a context for a requester. If one already exists for the requester, it logs and drops the old context.
- `lookup_dir_dump()` finds an existing context.
- `drop_dir_ctx()` removes all contexts for a node.
- `dlm_copy_master_names()` either starts from `ls_masters_list.next` or resumes after the RSB matching `inbuf/inlen`.
- When a response fills, it writes a zero-length record (`0x0000`) as the end-of-block marker and keeps the dump context.
- When the full list is complete, it writes `0xFFFF`, logs totals, removes the context, and frees it.

## Resource Lookup for Resume

`find_rsb_root()` first searches the active RSB rhashtable through `dlm_search_rsb_tree()`. If not found, it scans `ls_masters_list` directly as a fallback and logs when it has to use the root list. This fallback matters because directory dumps resume by name and need to recover the list cursor.

## Dependencies

This file ties together:

- `lock.c` through `dlm_master_lookup()` and `dlm_search_rsb_tree()`.
- Recovery communication through `rcom.h`.
- Membership state through `member.h`.
- Lockspace state and flags through `dlm_internal.h` and `lockspace.h`.

## Concurrency Notes

- `ls_masters_lock` protects the master resource list while names are copied.
- `ls_dir_dump_lock` protects dump context allocation, lookup, and removal.
- `dlm_recover_directory()` checks `dlm_recovery_stopped()` inside the chunk loop to abort promptly on membership/recovery changes.

## Research Notes

The directory protocol is intentionally cursor-based and restart-aware. The requester sends the last resource name it processed, and the responder verifies that its saved context still matches the current recovery sequence and last list node. This guards against stale chunk continuation after aborted or restarted recovery.
