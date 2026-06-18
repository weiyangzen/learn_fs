# sources/sync-backup/casync/src/cafileroot.c

## Purpose
Implements the tiny reference-counted `CaFileRoot` object that anchors a `CaLocation` to either a filesystem path, an fd, or both. It lets cached locations reopen origin files without embedding ownership of the original root directly in each location.

## Important APIs, Types, and Functions
`ca_file_root_new` validates that either `path` or `fd` is present and allocates a root with `n_ref = 1`. `ca_file_root_ref` and `ca_file_root_unref` implement manual reference counting. `ca_file_root_invalidate` marks a root stale and clears path/fd fields without freeing the object.

## Control Flow
Construction stores the fd and optionally duplicates the path. References are incremented by users such as `CaLocation`. Unref decrements and frees path/object when the count reaches zero. Invalidation clears reopen data and sets `invalidated`, causing later `ca_location_open` to fail with an unattached/stale root.

## State and Persistence Behavior
The object is in-memory state only. It does not close the stored fd on unref or invalidation; it sets `fd = -1`, so fd ownership is external. The persisted meaning is indirect: locations that reference an invalidated root can no longer be trusted to reopen files.

## Dependencies and Integration Points
Depends on `util.h` helpers (`new0`, `mfree`, `assert_se`). Integrated by `calocation.c` for root attachment and reopen validation.

## Risks
External fd ownership must be clear because this code does not close the fd. Invalidation is broad and permanently disables all attached locations. Reference counting is not atomic and is not thread-safe.

## Test Signals
Test path-only, fd-only, and path+fd roots; invalid constructor arguments; ref/unref lifetime; invalidation effects through `ca_location_open`; and leak checks for duplicated paths.
