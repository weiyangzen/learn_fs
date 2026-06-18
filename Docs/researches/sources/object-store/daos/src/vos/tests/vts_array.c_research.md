# sources/object-store/daos/src/vos/tests/vts_array.c

## Purpose

`vts_array.c` implements a small DAOS-array-like abstraction on top of raw VOS object operations. It is not a cmocka suite itself; it is a test utility used by other VOS tests that need array semantics without involving the full DAOS array layer.

## Important APIs, Types, And Functions

`struct vts_metadata` stores the object magic, record size, records per dkey stripe, and akey size. `struct vts_array` is the open handle state: OID, container handle, array and metadata IODs, dkey/akey backing buffers, recx and iov arrays, I/O chunk size, metadata, and a zero buffer used for extending size.

The exported API is `vts_array_alloc()`, `vts_array_free()`, `vts_array_open()`, `vts_array_reset()`, `vts_array_close()`, `vts_array_set_size()`, `vts_array_get_size()`, `vts_array_set_iosize()`, `vts_array_write()`, `vts_array_punch()`, and `vts_array_read()`. Internally, `array_init()`, `array_open()`, and `array_fini()` manage handle memory. `update_meta()` and `fetch_meta()` persist metadata as a single value under dkey zero/akey zero. `update_array()` and `fetch_array()` build one or more recxs for a single stripe.

## Control Flow

Allocation generates a `DAOS_OT_DKEY_UINT64` object ID, initializes a temporary array descriptor, and writes metadata at the creation epoch. Opening fetches metadata at `DAOS_EPOCH_MAX`, validates `ARRAY_MAGIC`, allocates per-open buffers, and returns a cookie-style `daos_handle_t`.

Reads, writes, and punches split logical array offsets into stripes of `vm_per_key` elements. Each stripe is stored under dkey `stripe + 1`, with the configured akey length. Partial stripe writes become `vos_obj_update()` calls with recxs. Whole-stripe punches call `vos_obj_punch()` on the dkey; partial punches call `update_array()` with `iod_size` zero. Size discovery uses `vos_obj_query_key()` with `DAOS_GET_DKEY | DAOS_GET_RECX | DAOS_GET_MAX`.

## State And Persistence Behavior

The abstraction persists only VOS object data: metadata single value and array extents partitioned by numeric dkeys. Open handles are process-local cookies and are invalidated by `array_fini()` clearing the magic. `vts_array_reset()` punches the whole object at an earlier epoch, writes new metadata at a later epoch, closes the old handle, and reopens it.

## Dependencies And Integration Points

It depends on `vts_io.h`, `vts_array.h`, VOS object update/fetch/query/punch/delete APIs, DAOS I/O descriptor types, and DAOS allocation/assertion helpers. The interface in `vts_array.h` lets test code model DAOS array behavior while staying in standalone VOS.

## Risks And Test Signals

The main risks are pointer arithmetic on `void *`, correct stripe boundary math, and allocation error cleanup. There is a likely copy/paste bug in `array_open()`: after allocating `va_iovs`, it checks `array->va_recx == NULL` instead of `array->va_iovs == NULL`. The utility has no direct tests in this file, so downstream array-like tests are the signal.
