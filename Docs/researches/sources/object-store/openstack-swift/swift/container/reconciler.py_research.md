# sources/object-store/openstack-swift/swift/container/reconciler.py

## Purpose
This module implements the container reconciler daemon and helper functions for misplaced object queues. It detects object listings whose storage policy does not match the container's current policy, queues them under `.misplaced_objects`, and later copies/deletes object data so the object lands in the correct policy while cleaning stale source entries.

## Important APIs, Types, and Functions
- `cmp_policy_info()`, `incorrect_policy_index()`, `translate_container_headers_to_info()`, and `best_policy_index()` decide which container policy information is authoritative across primary container responses, accounting for delete/recreate races.
- `get_reconciler_container_name()` buckets queue entries by object metadata timestamp rounded down to an hour.
- `get_reconciler_obj_name()` encodes queue object names as `<policy_index>:/<account>/<container>/<object>`.
- `get_reconciler_content_type()` maps queue operations to `application/x-put` or `application/x-delete`.
- `get_row_to_q_entry_translator()` converts broker misplaced rows into queue object records.
- `add_to_reconciler_queue()` writes queue entries directly to primary container servers and succeeds on majority.
- `parse_raw_obj()` decodes queue listing rows into reconciliation work items.
- `direct_get_container_policy_index()` queries primary container servers and caches majority-derived policy index briefly with `LRUCache`.
- `direct_delete_container_entry()` removes a queue object directly from container servers.
- `ContainerReconciler(Daemon)` owns the daemon config, internal client, queue iteration, object reconciliation, stats, process sharding, and run loop.

## Control Flow and Behavior
Queue insertion computes an hour bucket from the object's metadata timestamp, encodes the source policy and object path into the queue object name, chooses an operation content type, and sends direct PUTs to the misplaced-objects account using the replication network header. The queue entry's etag/hash carries the original object timestamp.

During reconciliation, `ContainerReconciler.reconcile()` iterates the current queue container first, then existing queue containers in reverse listing order. For each raw object it calls `parse_raw_obj()`, optionally filters by configured process modulo hash, and spawns `process_queue_item()` in an eventlet `GreenPool`.

`_reconcile_object()` first determines the container's current policy by direct HEAD majority. If the queue policy already matches, the item is done. It skips reconciliation while either source or destination policy is in part-power-increase state. It then checks destination metadata; if destination has a timestamp newer than or equal to the queue timestamp, the source can be tombstoned. Otherwise it fetches the source object from the queued policy. A queued DELETE with missing source ensures a tombstone in the destination policy; a PUT copies the source object to the destination with a slightly later timestamp and then tombstones the source.

Successful work calls `pop_queue()`, which deletes the queue object using a timestamp later than both queue record and queue object timestamps. Failures leave the queue entry for retry. Old empty queue containers are deleted after `reclaim_age`.

## State and Persistence
Persistent state lives in `.misplaced_objects` account containers and in object/container rings. Queue container names are hourly epoch buckets. Queue object names encode source policy and object path, while content type encodes operation and etag/hash encodes the source timestamp. The daemon holds transient `stats`, `last_stat_time`, config values (`reclaim_age`, `interval`, `concurrency`, `processes`, `process`), and an `InternalClient`.

## Dependencies and Integration Points
The reconciler depends on container rings, object rings via storage policies, `InternalClient`, direct container client operations, `ContainerBroker.get_misplaced_since()` indirectly through queue translation, timestamp utilities, `MISPLACED_OBJECTS_ACCOUNT`, replication network headers, Swift constraints, and daemon runner utilities. It integrates with container updater/reconciler queue producers and object-server policy placement.

## Risks and Edge Cases
- Policy comparison is intentionally nuanced around deleted and recreated containers; incorrect ordering can move objects to stale policies.
- Direct client majority failures cause retries and can delay cleanup.
- Reconciliation is skipped during part-power increase because partition layout is unstable.
- Timestamp offsets (`slightly_later_timestamp`) are critical to avoid overwriting newer user writes while ensuring cleanup tombstones win over stale rows.
- If source data is unavailable until `reclaim_age` expires, the daemon eventually logs critical `lost_source` and drops the queue item as handled.
- Invalid queue object names or content types are logged and skipped, leaving bad records unless separately removed.
- Process modulo filtering must match across multiple daemon processes to avoid duplicate or missed work.

## Test Signals
Tests should cover policy-info comparison for deleted/recreated containers, majority success/failure for queue insertion and policy HEADs, queue name parsing, PUT versus DELETE reconciliation, newer destination handling, missing/old source retry versus expiration, PPI skip behavior, queue popping timestamps, old empty container cleanup, process sharding by hash, stats counters, and exception containment in `reconcile_object()` and `run_once()`.
