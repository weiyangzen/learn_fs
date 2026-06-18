# File Research: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayout.c

## Purpose

Implements the NFSv4 pNFS flexfile layout driver. It decodes layout segments, manages mirrors and data-server stripes, routes reads/writes/commits to DS clients or MDS fallback, records layout errors/statistics, and registers the `LAYOUT_FLEX_FILES` layoutdriver.

## Main Entry Points

- `ff_layout_alloc_layout_hdr()` / `ff_layout_free_layout_hdr()`: allocate and release flexfile per-layout state.
- `ff_layout_alloc_lseg()` / `ff_layout_free_lseg()` / `ff_layout_add_lseg()`: decode, cache, merge, sort, and release flexfile layout segments.
- `ff_layout_pg_init_read()` / `ff_layout_pg_init_write()` / `ff_layout_pg_test()`: pageio setup and coalescing rules for striped DS I/O.
- `ff_layout_read_pagelist()` / `ff_layout_write_pagelist()`: initiate async DS read/write RPCs or localio.
- `ff_layout_commit_pagelist()` / `ff_layout_initiate_commit()`: send unstable-write commits to the right DS stripe.
- `ff_layout_async_handle_error_v3()` / `ff_layout_async_handle_error_v4()`: translate DS/RPC errors into retry, pNFS resend, MDS fallback, or fatal I/O.
- `ff_layout_prepare_layoutreturn()` / `ff_layout_encode_layoutreturn()`: collect DS errors and stats for LAYOUTRETURN.
- `ff_layout_prepare_layoutstats()` and stats encoding helpers: prepare LAYOUTSTATS payloads.
- `nfs4flexfilelayout_init()` / `nfs4flexfilelayout_exit()`: register/unregister the layout driver.

## Control Flow And State

Layout segment allocation decodes XDR layout data: stripe unit, mirror count, per-mirror DS stripe count, device IDs, efficiencies, DS stateids, filehandle versions, and per-DS credentials. Mirrors are deduplicated at the layout level by matching device IDs and filehandles, refcounted, then sorted by summed efficiency.

Read pageio selects one mirror/stripe, preferring available device IDs and falling back to other mirrors before MDS fallback. Write pageio prepares every mirror because RW flexfile layouts require all mirrors. Stripe boundaries limit request coalescing. DS I/O setup chooses filehandles, stateids, credentials, DS RPC clients, localio handles when available, and version-specific call ops.

Completion paths update layoutstats, handle NFSv3/NFSv4 protocol errors, record DS errors, mark device IDs unavailable or reachable, resend to another pNFS mirror when possible, or reset through MDS. Successful writes and commits trigger layoutcommit unless the layout says not to. Layoutreturn and layoutstats encode accumulated IO error records and latency/count data into flexfile layoutupdate XDR.

## Dependencies

Depends on the pNFS core, NFS pageio/read/write/commit infrastructure, NFSv4 session and stateid handling, DS deviceid cache, RPC task/call ops, fscache-independent localio helpers, `nfs42` LAYOUTERROR/LAYOUTSTATS support, and structures declared in `flexfilelayout.h`.

## Risks

The driver is concurrency-heavy: mirror lists are protected by inode locks, per-mirror stats by mirror locks, credentials through RCU, and DS device IDs by pNFS caches. Error handling must avoid infinite pNFS/MDS retry loops while preserving layoutreturn diagnostics. XDR decoding must reject invalid mirror/stripe counts and bad filehandles, because counts can drive large allocations. Layoutstats and LAYOUTRETURN share mirror references and private XDR cleanup paths, so missed refcount/free handling can leak or use stale mirror state.
