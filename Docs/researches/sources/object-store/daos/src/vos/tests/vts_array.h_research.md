# sources/object-store/daos/src/vos/tests/vts_array.h

## Purpose

`vts_array.h` declares the VOS test-array helper API implemented in `vts_array.c`. The comments describe it as a convenience library for DAOS-array-like behavior on one standalone VOS target.

## Important APIs And Types

The header includes `<daos_srv/vos.h>` and exposes only opaque `daos_handle_t` array handles and `daos_unit_oid_t` object IDs. The lifecycle API is `vts_array_alloc()`, `vts_array_open()`, `vts_array_reset()`, `vts_array_close()`, and `vts_array_free()`. The data API is `vts_array_set_iosize()`, `vts_array_set_size()`, `vts_array_get_size()`, `vts_array_write()`, `vts_array_punch()`, and `vts_array_read()`.

## Control Flow And Integration

Callers allocate an array object in a VOS container at a creation epoch, open it into a handle, optionally tune I/O chunking, then perform epoch-addressed reads, writes, punches, and size changes. Reset requires a punch epoch lower than the recreate epoch. Free deletes the underlying VOS object.

## State And Persistence Behavior

The header intentionally hides `struct vts_array`; state lives in the implementation and in VOS object metadata. All operations are epoch-aware, so callers can test MVCC/aggregation behavior over array-like records.

## Dependencies, Risks, And Test Signals

This is a narrow test helper contract. Risks come from callers assuming full DAOS array semantics; the implementation is simpler and stores metadata/data through raw VOS. Test signal is indirect: any suite using these functions should prove stripe splitting, size queries, and punch behavior.
