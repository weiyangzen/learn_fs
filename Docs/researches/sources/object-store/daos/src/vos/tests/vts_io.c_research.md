# sources/object-store/daos/src/vos/tests/vts_io.c

## Purpose
`vts_io.c` is the central VOS object IO test suite and shared implementation behind the declarations in `vts_io.h`. It creates the reusable `io_test_args` fixture, generates object IDs and keys for multiple DAOS object-class key layouts, and exercises the VOS update, fetch, punch, iteration, query-key, checksum, zero-copy, object-index, and object-cache paths. The file is test-facing but reaches into internal VOS, BIO, checksum, DTX, and object-cache APIs to validate persistence-tree behavior below the public object API layer.

## Important APIs, Types, And Functions
The key exported helpers are `setup_io`, `teardown_io`, `test_args_reset`, `vts_key_gen`, `set_iov`, `gen_rand_epoch`, `gen_oid`, `gen_oid_stable`, `inc_cntr`, `io_test_obj_update`, `io_test_obj_fetch`, and `run_io_test`. Static fixture state includes `vts_epoch_gen`, `vts_cntr`, fixed integer akey values, `last_dkey`, `last_akey`, and `vts_nest_iterators`.

`test_args_init` initializes a `vos_test_ctx`, chooses object type-dependent key sizing, prepares fixed akeys for single-value and array modes, and records the generated pool filename. `setup_io` also creates a VOS timestamp table with `vos_ts_table_get(true)`, while `teardown_io` frees/reallocates it before finalizing the VOS test context.

The main IO wrapper pair abstracts normal and zero-copy paths. `io_test_obj_update` optionally computes checksums, supports array remove when `TF_DELETE` is set, calls `vos_obj_update` for ordinary writes, or drives `vos_update_begin`, `bio_iod_prep`, `bio_iod_copy`, `bio_iod_post`, and `vos_update_end` for zero-copy writes. `io_test_obj_fetch` similarly chooses ordinary fetch via `io_test_vos_obj_fetch` or a zero-copy fetch path using `vos_fetch_begin`, BIO copy from persistent media, and `vos_fetch_end`. `io_test_vos_obj_fetch` additionally verifies fetched checksum metadata through `ds_csum_add2iod`, `ds_iom_create`, and `daos_csummer_verify_iod`.

## Control Flow
`run_io_test` first runs integer-object-class tests with `DAOS_OT_MULTI_UINT64`, then runs general IO and iterator suites over caller-provided object types. `run_oclass_tests` derives readable key-type labels, runs `io_tests`, then runs `iterator_tests` twice with nested iterator mode disabled and enabled. `run_single_class_tests` runs object-index, object-cache, key-query, large single-value, and checksum metadata tests.

The common update/fetch flow is `io_update_and_fetch_dkey`: generate dkey/akey unless overwriting or punching, configure either `DAOS_IOD_SINGLE` or `DAOS_IOD_ARRAY`, write through `io_test_obj_update`, update counters, fetch through `io_test_obj_fetch`, and compare buffers and record size. This powers simple one-key, many-key, overwrite, near-epoch, and iterator setup tests.

Iterator control flow is split by hierarchy. `io_obj_iter_test` prepares a dkey iterator, optionally sets fixed akey filters and anchor probes, then calls `io_akey_iterate`, which may set parent iterator handle for nested iteration and calls `io_recx_iterate`. Range and reverse-range tests create epochs around a selected range and assert only in-range records are enumerated. `vos_iterate_test` exercises the higher-level recursive iterator API with filter, pre, and post callbacks that request yield, skip, and abort actions, then checks exact callback counts.

## State And Persistence Behavior
The fixture creates and destroys real VOS pool/container state through `vts_ctx_init` and `vts_ctx_fini`. The tests rely on persisted object trees, epoch visibility, punches, and holes. Key state is deliberately reused through `last_dkey` and `last_akey` for overwrite and punch scenarios. Stable OID generation uses deterministic prime increments to support broad conditional collision-like coverage in other suites.

Object-cache tests manipulate the thread-local object cache (`vos_tls_get`, `vos_obj_cache_create`, `vos_obj_cache_destroy`) and validate hold/release conflicts for discard, aggregation, visible read, and create intents across two containers. Key-query tests build integer-key trees, punch records, akeys, dkeys, and objects, and validate `vos_obj_query_key` min/max dkey/akey/recx results and max-write epoch behavior. Checksum tests validate both single-value checksum fetch and array recx checksum metadata, including the case where recx entries have no stored checksums and the checksum info list must be empty.

## Dependencies And Integration Points
The file depends on `vts_io.h`, `vts_array.h`, `vts_common.h` transitively, DAOS object/checksum APIs, server checksum helpers, VOS internals, BIO helpers, CMocka, and DTX helpers such as `vts_dtx_begin`/`vts_dtx_end`. It integrates with the broader VOS test runner through `run_io_test`, which supplies object types and key counts. Other VOS tests reuse the exported fixture and helper wrappers.

## Risks And Test Signals
The suite is intentionally broad and can be expensive: `VTS_IO_KEYS` reaches 100K unless tracing or Valgrind reduces it, and `gang_sv_test` allocates 27 MB buffers. Many tests assume exact iterator callback counts, epoch ordering, and object tree behavior, so legitimate iterator implementation changes require test updates. The zero-copy paths touch internal BIO descriptors directly, which is useful coverage but tightly couples the tests to VOS/BIO internals. Strong signals include CMocka assertions for return codes, buffer equality, iterator counts, `-DER_NONEXIST`, `-DER_REC2BIG`, checksum identity, and transactional punch/query behavior.
