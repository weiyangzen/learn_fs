# sources/user-network-fs/nfs-ganesha/src/include/nfs_dupreq.h

## Purpose

`nfs_dupreq.h` defines the duplicate request cache (DRC), which prevents repeated non-idempotent NFS requests from being processed multiple times and enables replay/resume behavior after client retries.

## Important APIs, Types, and Functions

`drc_t` stores DRC type, red-black lookup tree, FIFO completed queue, mutex, partition/cache sizes, refcount, retry window, and TCP recycle metadata. `dupreq_entry_t` stores request identity, hash key, completion flag, refcount, result pointer, request result code, duplicate count, and a queue of up to `DUPREQ_MAX_DUPES` suspended duplicate requests. APIs include `dupreq2_pkginit`, `drc_get_tcp_drc`, `drc_release_tcp_drc`, `nfs_dupreq_start`, `nfs_dupreq_finish`, `nfs_dupreq_delete`, `nfs_dupreq_rele`, `for_each_tcp_drc`, and `get_tcp_drc_recycle_qlen`.

## Control Flow

Dispatch calls `nfs_dupreq_start` before protocol execution. New requests proceed, completed duplicates replay cached results, in-flight duplicates are queued/suspended, and failures can resume queued retries. Completion calls `nfs_dupreq_finish`; retryable drops/auth errors use `nfs_dupreq_delete` to allow reprocessing.

## State and Persistence Behavior

DRC state is in-memory per connection/address and stores completed response data until eviction. It is not durable across restart. Cached responses and suspended requests affect externally visible at-most-once behavior.

## Dependencies and Integration Points

It depends on NFS core/data types, address utilities, pools, red-black trees, queues, and async dispatch. It integrates with RPC worker dispatch, XDR response storage, metrics, and transport lifecycle.

## Risks and Test Signals

Risks include refcount leaks, replaying mutable response buffers after free, hash/checksum collisions, deadlocks between DRC and entry locks, unbounded suspension if duplicate queues fail to drain, and TCP reconnect identity mistakes. Tests should cover concurrent duplicate non-idempotent requests, send-failure retry resume, eviction watermarks, UDP/TCP v3/v4 differences, recycle queue behavior, and request result replay correctness.
