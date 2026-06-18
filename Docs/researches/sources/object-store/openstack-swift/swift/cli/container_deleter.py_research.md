# sources/object-store/openstack-swift/swift/cli/container_deleter.py

Purpose: enqueues async-delete jobs for a range of objects in one container, letting the object expirer delete them later while listings may still show them until expiration processing catches up.

Important APIs: `OBJECTS_PER_UPDATE`, `make_delete_jobs()`, `mark_for_deletion()`, and `main()`. `make_delete_jobs()` creates expirer queue update rows using `build_task_obj()` and `ASYNC_DELETE_TYPE`. `mark_for_deletion()` is usable as a generator for progress and retry markers.

Control flow: the tool lists objects through `InternalClient.iter_objects()` with marker/end-marker/prefix. It batches up to 10,000 object names, builds async-delete rows at a single timestamp, sends an internal `UPDATE` to `.expiring_objects/<timestamp>`, and yields progress periodically with the last processed object. `main()` constructs an `InternalClient` and prints progress or final count.

State and persistence: writes expirer queue objects via internal Swift requests; it does not delete user objects directly. Timestamp selection controls delete task identity and target expirer container.

Dependencies and integration: depends on `InternalClient`, object-expirer task naming, Swift timestamps, and private backend headers.

Risks: duplicates may be enqueued on retry before the last marker; the code intentionally reports the last object to reduce that. The default `--timestamp` is created when argparse is built, not at loop time, but `main()` constructs the parser per invocation. Large containers can produce sustained internal load.

Test signals: cover job payload shape, batching, generator vs count mode, marker/end-marker/prefix forwarding, backend headers, failed internal requests, and retry progress semantics.
