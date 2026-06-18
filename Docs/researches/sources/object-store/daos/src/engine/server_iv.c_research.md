# sources/object-store/daos/src/engine/server_iv.c

## Purpose
`server_iv.c` implements DAOS server-side IV support on top of CART IV. It manages IV class registration, namespace lifecycle, key packing/unpacking, entry caches, leader-aware fetch/update/invalidate callbacks, lazy asynchronous operations, retry behavior, and namespace cleanup for pool service state.

## Important APIs, Types, and Functions
Key APIs include `ds_iv_class_register`, `ds_iv_class_unregister`, `iv_key_pack`, `iv_key_unpack`, `ds_iv_ns_create`, `ds_iv_ns_update`, `ds_iv_ns_start`, `ds_iv_ns_stop`, `ds_iv_ns_leader_stop`, `ds_iv_ns_cleanup`, `ds_iv_ns_reint_prep`, `ds_iv_ns_id_get`, `ds_iv_fetch`, `ds_iv_update`, `ds_iv_invalidate`, `ds_iv_init`, and `ds_iv_fini`. The CART callback table `iv_cache_ops` wires DAOS behavior into IV fetch/update/refresh/hash/get/put/pre-sync operations.

## Control Flow
Classes are registered by mapping a DAOS class id to DAOS class ops and a CART IV ops slot. Namespaces are created with a pool UUID and CART group, then assigned a monotonically increasing local namespace id. Fetch/update/invalidate operations set the key version/rank, pack the key, call CART IV, wait on an Argobots future, and optionally retry retryable, not-leader, and busy errors. Lazy sync clones the key/value and launches an async ULT on the system xstream.

## State and Persistence Behavior
Global process state includes class lists, namespace lists, namespace ids, tree topology, and dynamically grown CART IV class array. Per namespace state includes pool UUID, CART namespace handle, master rank/term, refcount, stop flag, condition variable, and cached `ds_iv_entry` list. Entries cache values and validity; class callbacks may customize allocation, update, refresh, validation, destruction, and private get/put state. State is memory-resident cache/coherency metadata, not directly persistent.

## Dependencies and Integration Points
The file depends on CART IV, Argobots futures/conditions, DAOS IV class definitions, DAOS SGL helpers, server rank/version/check-mode helpers, and scheduler sleep/ULT creation. Pool/container/object subsystems register IV classes and use namespaces to distribute service and object metadata coherently across ranks.

## Risks
Refcounting is subtle: namespace references are held across in-flight operations and callbacks, `ivc_on_get` pairs with `ivc_on_put`, and stop waits for refcount drain. Comments note a possible leak if private-entry allocation fails after `ivc_value_alloc`. Leader changes return `-DER_NOTLEADER` or `-DER_GRPVER` in specific paths; retry loops can run indefinitely until namespace stop. Key comparison defaults to equality when no class comparator exists, so class ops must be correct for nontrivial keys.

## Test Signals
Tests should cover class registration reuse of CART ops, duplicate class ids, namespace create/update/stop/refcount drain, fetch forwarding on non-leader, update rejection for stale master rank, lazy update cloning and cleanup, retry behavior under `-DER_NOTLEADER` and retryable errors, reintegration prep deleting selected IV classes, and leak checks around `ivc_on_get` failures.
