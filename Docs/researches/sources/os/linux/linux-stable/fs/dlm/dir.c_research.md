# File Research: sources/os/linux/linux-stable/fs/dlm/dir.c

## Purpose
`dir.c` implements the DLM directory: the mapping from resource-name hashes to directory nodes and, through directory records, to resource master nodes. It also supports directory reconstruction during lockspace recovery.

## Main Interfaces
- `dlm_hash2nodeid()` maps a resource hash to a directory node using the upper 16 hash bits, `ls_total_weight`, and `ls_node_array`.
- `dlm_dir_nodeid()` returns `rsb->res_dir_nodeid`.
- `dlm_recover_dir_nodeid()` recomputes directory node ids for RSBs on a recovery root list.
- `dlm_recover_directory()` rebuilds local directory records by requesting master-name dumps from other members.
- `dlm_copy_master_names()` serves those name-dump requests to other nodes.

## Directory Recovery
`dlm_recover_directory()` iterates current members other than self, repeatedly calls `dlm_rcom_names()`, and parses returned big-endian name-length/name records. It treats:
- `0xFFFF` as end-of-dump for a node.
- `0` as end-of-buffer/chunk.

For each name, it calls `dlm_master_lookup(..., DLM_LU_RECOVER_DIR, ...)` to add or verify a directory record. It logs inconsistent cases where an existing directory entry maps the name to a different master than the member claiming it. On success it sets `DLM_RS_DIR`.

If `LSFL_NODIR` is set, recovery skips directory rebuilding and still marks directory recovery complete.

## Name Dump Serving
`dlm_copy_master_names()` walks `ls_masters_list` under `ls_masters_lock`, selecting only RSBs for which the requesting node is the directory node. It emits a sequence of big-endian length/name records into the provided output buffer, stopping early with a `0` record if the next record plus terminator would not fit. At the end of the list it emits `0xFFFF`.

The function tracks multi-message dump state with `struct dlm_dir_dump` objects stored on `ls_dir_dump_list` under `ls_dir_dump_lock`. Each context records the recovery sequence, requester node, last list position, and sent counters. The code uses this state to continue dumps and sanity-check that recovery sequence/list position did not drift.

## Dependencies
Uses RCOM recovery messaging from `rcom.h`, member lists from `member.h`, lock/RSH lookup helpers from `lock.h`, and lockspace recovery status helpers.

## Concurrency
The local RSB table is read via `dlm_search_rsb_tree()` under `ls_rsbtbl_lock` in `find_rsb_root()`, with a fallback scan of `ls_masters_list`. Directory dump contexts use a separate rwlock. Master-list iteration is protected by `ls_masters_lock`.

## Risks and Notes
The dump protocol is stateful and assumes the peer will continue using the last name/length. If the context is missing or the recovery sequence changed, the function logs and aborts the chunk without writing a structured error into `outbuf`. Buffer parsing in recovery is defensive about record length and maximum DLM resource-name length.
