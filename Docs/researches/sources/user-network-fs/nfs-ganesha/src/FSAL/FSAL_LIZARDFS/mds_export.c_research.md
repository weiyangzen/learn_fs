# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/mds_export.c

Purpose: Implements LizardFS pNFS MDS export/module operations: GETDEVICEINFO, device list, layout type/block/segment reporting, loc-body and device-address sizing, and DS address selection from LizardFS chunkserver/chunk metadata.

Important APIs and types: Public hooks are `lzfs_fsal_export_ops_pnfs()` and `lzfs_fsal_ops_pnfs()`. The main operation is `lzfs_fsal_getdeviceinfo()`. Helpers include chunkserver sorting/dedup/removal/shuffle functions and DS list encoders `lzfs_int_fill_chunk_ds_list()` and `lzfs_int_fill_unused_ds_list()`.

Control flow: GETDEVICEINFO validates FILE layout type, uses `deviceid->device_id2` to find the matching export, retrieves chunk info for `deviceid->devid`, retrieves and randomizes live chunkserver IPs, computes a stripe count bounded by `LZFS_BIGGEST_STRIPE_COUNT`, encodes stripe indices, then encodes multipath DS entries. For chunks with known parts it prefers standard part replicas, then non-standard replicas, and pads with randomized chunkservers up to three addresses. Remaining stripe entries are filled from the randomized server list.

State and persistence: No persistent state is modified. Device info reflects current LizardFS chunk layout and chunkserver availability. Randomized DS ordering creates per-call variability.

Dependencies and integration: Depends on Ganesha pNFS/XDR utilities, module export list, LizardFS chunk/chunkserver APIs, constants from `lzfs_internal.h`, and `op_ctx->creds`. Export ops are enabled from `main.c` when MDS pNFS is supported.

Risks: The custom `remove_if()` copies from `j` to `i`, which is the reverse of the usual compaction direction and appears likely to corrupt filtering results. Duplicate-IP predicate assumes sorted array and pointer arithmetic against previous element. `liz_destroy_chunkservers_info(chunkserver_info)` is called before filtering and freeing labels; correctness depends on LizardFS API semantics. Randomization uses `rand()` without explicit seeding/thread-safety. Device-address size is heuristic but large.

Test signals: GETDEVICEINFO for disconnected servers, duplicate IPs, empty chunkserver list, files with more than 4096 chunks, chunks with fewer than three replicas, non-standard chunk parts, multi-export device ids, XDR buffer boundaries, and repeated calls to check DS distribution stability.
