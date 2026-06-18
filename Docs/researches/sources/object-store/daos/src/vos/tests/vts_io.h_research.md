# sources/object-store/daos/src/vos/tests/vts_io.h

## Purpose
`vts_io.h` is the shared interface for the VOS IO-oriented test suites. It centralizes constants, flags, fixture state, counters, and helper prototypes used by `vts_io.c`, punch-model tests, MVCC tests, corruption-mark tests, aggregation tests, and array helpers.

## Important APIs, Types, And Functions
The header defines update/fetch sizing constants such as `UPDATE_DKEY_SIZE`, `UPDATE_AKEY_SIZE`, `UPDATE_BUF_SIZE`, `UPDATE_REC_SIZE`, checksum buffer sizes, and the default IO key counts. `enum vts_test_flags` controls test behavior for iterator anchors, zero-copy, overwrite, punch, record extents, fixed akeys, value/checksum use, deletion, and disabled tests.

`struct io_test_args` is the central fixture passed through CMocka state. It stores the VOS test context, current object ID, optional additional container UUID/handle, epoch range lower bound, flags, default dkey/akey strings and sizes, custom test-private state, object type, container creation step, and replay/checkpoint failure toggles. `struct vts_counter` tracks dkeys, fixed-akey dkeys, oids, and punch operations for iterator verification.

Declared helper APIs include object and epoch generation (`gen_rand_epoch`, `gen_oid`, `reset_oid_stable`, `gen_oid_stable`), counter updates, fixture setup/teardown, argument reset, key generation, simple iov setup, and object update/fetch wrappers. It also declares `update_value` and `fetch_value` from `vts_aggregate.c`.

## Control Flow
The header itself has no runtime control flow beyond the inline `hash_key`. Test files include it to share fixture setup, generate compatible object/key layouts, and call `io_test_obj_update`/`io_test_obj_fetch` instead of open-coding all VOS IO variants. `hash_key` interprets integer keys as a `uint64_t` when requested and otherwise uses `d_hash_string_u32`.

## State And Persistence Behavior
The important state contract is the shape of `io_test_args`: each test starts with a VOS pool/container in `ctx`, uses `oid` and type-aware dkey/akey fields to address persistent trees, and may attach per-test data through `custom`. The flags influence whether the backing VOS operation writes arrays or single values, checksums, zero-copy BIO data, deletion/removal records, and iterator anchor handling.

## Dependencies And Integration Points
The header pulls in CMocka, DAOS common/VOS server APIs, `vos_obj.h`, and `vos_internal.h`, so users of this fixture can test internal VOS behavior rather than only public client APIs. It is included by `vts_io.c`, `vts_mark.c`, `vts_mvcc.c`, `vts_pm.c`, and other VOS tests.

## Risks And Test Signals
Because this header exposes internal VOS types into many tests, changes to `struct io_test_args`, flag bits, or helper prototypes have broad compile and behavioral impact. Integer-key hashing assumes the iov buffer is at least eight bytes when `flag` is set. The test signal is mostly indirect: successful compilation of all dependent tests and correct runtime behavior of the shared fixture wrappers.
