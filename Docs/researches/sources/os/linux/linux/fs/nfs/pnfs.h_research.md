# File Research: sources/os/linux/linux/fs/nfs/pnfs.h

## Purpose
`pnfs.h` defines the internal pNFS client interface shared by NFS core code and pNFS layout drivers. It declares layout-driver operations, layout and deviceid structures, commit helper contracts, data-server structures, exported pNFS functions, range helpers, and no-op stubs for builds without NFSv4 support.

## Core Data Structures
- `struct nfs4_pnfs_ds_addr`: one data-server address, including sockaddr, length, netid, transport, human-readable address string, and list linkage.
- `struct nfs4_pnfs_ds`: cached data-server object with address list, network namespace, `nfs_client`, refcount, and connection state.
- `struct pnfs_layout_segment`: one cached layout range with list nodes, layoutcommit list, commit arrays, range, refcount, sequence, flags, and parent layout header.
- `struct pnfs_layout_hdr`: per-inode layout cache, with refcount, outstanding layoutget count, client/server list links, segment lists, return lists, flags, stateid, seq barrier, return info, last-write byte, credential, and inode.
- `struct pnfs_device` and `struct pnfs_devicelist`: GETDEVICEINFO/GETDEVICELIST transport containers.
- `struct nfs4_deviceid_node`: global deviceid cache entry keyed by layout driver, NFS client, and deviceid.

## Layout Driver Contract
`struct pnfs_layoutdriver_type` is the main plugin ABI for pNFS layout drivers. It includes hooks for:
- Mount setup/cleanup: `set_layoutdriver`, `clear_layoutdriver`.
- Layout object allocation/free: `alloc_layout_hdr`, `free_layout_hdr`, `alloc_lseg`, `free_lseg`, optional `add_lseg`.
- Layoutreturn and layoutcommit preparation/cleanup.
- Pageio read/write operation tables and data-server commit info.
- Data I/O dispatch: `read_pagelist`, `write_pagelist`.
- Deviceid allocation/free.
- Layoutstats preparation.
- I/O cancellation on recalled segments.

## Commit Contract
`struct pnfs_commit_ops` defines generic data-server commit behavior:
- Allocate/release per-layout data-server commit info.
- Commit data-server page lists.
- Mark and clear requests that must commit to a data server.
- Scan commit lists, and recover commit requests back to generic retry lists.

## Flags and Modes
- Segment flags include valid, return-on-close, layoutcommit, layoutreturn, and unavailable.
- Layout header flags include failed RO/RW layoutget, bulk recall, layoutreturn in progress/locked/requested, invalid stateid, first layoutget, inode freeing, hashed, and drain.
- Layout-driver policy flags include layoutreturn on setattr, layoutreturn on error, read-whole-page, and layoutget-on-open.
- Destroy modes distinguish invalidation, bulk return, and file bulk return.
- Deviceid flags distinguish invalid, temporarily unavailable, and no-cache deviceids.

## Exported Functions
The header declares pNFS entry points implemented in `pnfs.c`, `pnfs_dev.c`, and `pnfs_nfs.c`, including:
- Layout driver registration and selection.
- Layout update, processing, invalidation, return, return-on-close, reboot handling, and layoutcommit.
- Generic pNFS pageio read/write initialization, cleanup, tests, and submission.
- Data-server commit helpers.
- Deviceid lookup, deletion, availability marking, purge, and invalidation.
- Data-server address decoding, cache insertion, connection, and release.
- Layoutget-on-open preparation/parse/release.
- Layoutstats reporting.

## Inline Helpers
- `nfs_have_layout()`, `pnfs_layout_is_valid()`, `pnfs_enabled_sb()`, `pnfs_is_valid_lseg()`.
- Reference helpers: `nfs4_get_deviceid()`, `pnfs_get_lseg()`.
- Commit wrappers: `pnfs_commit_list()`, `pnfs_get_ds_info()`, `pnfs_init_ds_commit_info*()`, `pnfs_release_ds_info()`, `pnfs_mark_request_commit()`, `pnfs_clear_request_commit()`, `pnfs_scan_commit_lists()`, `pnfs_recover_commit_reqs()`.
- Policy wrappers: `pnfs_ld_layoutret_on_setattr()`, `pnfs_ld_read_whole_page()`, `pnfs_sync_inode()`, `pnfs_layoutcommit_outstanding()`, `pnfs_return_layout()`, `pnfs_use_threshold()`.
- Range arithmetic helpers: offset end/length calculation, range copy, exclusive-end calculation, range intersection, and request/segment intersection.
- `pnfs_lseg_cancel_io()` delegates cancellation to the layout driver if provided.

## Conditional Compilation
- Under `CONFIG_NFS_V4`, the real pNFS declarations are active.
- Without `CONFIG_NFS_V4`, the header provides no-op or false/zero stubs so generic NFS code can compile without pNFS support.
- `pnfs_report_layoutstat()` is real only with `CONFIG_NFS_V4_2`; otherwise it returns success without work.

## Invariants and Risks
- Layout drivers must provide at least `alloc_lseg` and `free_lseg`; registration rejects drivers without them.
- Refcount helpers assume objects are already valid and externally synchronized where required.
- Range helpers use exclusive-end semantics in several places; callers must not mix them with inclusive-end assumptions.
- Stub behavior means callers must rely on helpers rather than open-coding pNFS checks if they need NFSv4-disabled builds to remain correct.
