# sources/object-store/openstack-swift/swift/obj/watchers/dark_data.py

## Purpose
This module implements an optional object-auditor watcher that detects "dark data": object data files present on object nodes but absent from container listings. The watcher is disabled by default and must be enabled in object-server configuration. It can log, delete, or quarantine dark objects, but its own comments warn about significant performance impact and recommend starting with logging.

## Important APIs, Types, and Functions
`ContainerError` marks container lookup uncertainty. `DarkDataWatcher` is the plugin class with the auditor watcher lifecycle methods `start()`, `see_object()`, and `end()`, plus `policy_based_object_handling()`. `get_info_1(container_ring, obj_path)` is the lookup helper that queries container servers, follows shard namespaces recursively, and returns an object row, `None`, or raises `ContainerError`.

## Control Flow
Construction loads the container ring from `/etc/swift`, normalizes `action` to `log`, `delete`, or `quarantine`, and reads `grace_age` with a default of one week. `start()` records whether the auditor pass is a zero-byte-file pass (`ZBF`) and resets counters. `see_object()` ignores ZBF passes, skips recently written objects still within the grace age, then asks `get_info_1()` whether the object name appears in the appropriate container or shard. Unknown container-server state increments `tot_unknown`. Missing rows increment `tot_dark` and invoke the configured action. Found rows increment `tot_okay`. `end()` logs totals for non-ZBF passes.

`get_info_1()` splits the object path into account, container, and object. Its nested `check_container()` asks all container nodes for either automatic records or, on repeated visits, object records to break shard loops. It uses `direct_get_container()` with `prefix`, `limit=1`, `includes`, `states=listing`, and `X-Backend-Record-Type`. Shard responses are converted to `Namespace` objects and recursively queried. Only if every contacted container server agrees that the object is absent does it return `None`; any client/timeout errors raise `ContainerError`.

## State and Persistence Behavior
The watcher maintains per-pass counters in memory. The configured `delete` action removes the entire object data directory with `shutil.rmtree()`. The `quarantine` action raises `QuarantineRequest` so auditor infrastructure handles quarantine. The `log` action is non-mutating. No cache or database state is written by this module.

## Dependencies and Integration Points
It integrates with object auditor watcher hooks, direct container-client calls, the container ring, Swift `Namespace` shard records, object metadata fields `name` and `X-Timestamp`, and auditor quarantine semantics. It assumes object nodes have access to container ring data.

## Risks and Edge Cases
The performance risk is high because each eligible object may fan out to all container replicas and possibly shard containers. Container-server errors intentionally suppress dark-data decisions, so outages create false negatives. Sharded containers can produce misplaced rows or loops; the visited set and forced object-record lookup mitigate loops but not all stale namespace cases. The hardcoded `/etc/swift` ring path ignores a configured `swift_dir`. Deleting dark data is destructive, particularly if container listings are stale or sharding is in transition.

## Test Signals
Useful tests cover grace-age skipping, ZBF no-op behavior, action handling, unknown action fallback, all-replica absence, partial container failure returning unknown, shard recursion, loop prevention with repeated containers, and destructive action isolation. Probe tests should exercise sharded containers before enabling delete behavior.
