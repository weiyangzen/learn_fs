# sources/object-store/daos/src/vos/tests/vts_checksum.c

## Purpose

`vts_checksum.c` validates checksum storage and retrieval for VOS array records and unit-tests EVT checksum helper functions. It ensures VOS returns checksum metadata aligned with fetched physical bio vectors, correctly handles holes, and marks corrupted extents so fetch fails with checksum errors.

## Important APIs, Types, And Functions

`struct extent_key` captures container handle, object ID, and generated dkey/akey buffers. `extent_key_from_test_args()` maps `io_test_args` into VOS keys and OID. `struct recx_config`, `struct expected_biov`, and `struct test_case_args` describe update/fetch extents, checksum counts, expected bio-vector prefix/suffix trimming, and hole counts.

`csum_for_arrays_test_case()` is the core harness. It builds `dcs_iod_csums`, writes array extents with `vos_obj_update()`, uses `vos_fetch_begin()` to inspect the VOS I/O handle, and compares returned `dcs_ci_list` checksums against the original `dcs_csum_info` buffers via `cia_idx` helpers. Corruption tests use `vos_iterate()` plus `VOS_ITER_PROC_OP_MARK_CORRUPT` and verify `BIO_ADDR_IS_CORRUPTED()`.

EVT helper tests cover `evt_csum_count()`, `evt_csum_buf_len()`, `evt_entry_align_to_csum_chunk()`, and `evt_entry_csum_update()`.

## Control Flow

Ten checksum array cases cover single chunks, multiple extents, one extent fetched as many, many fetched as one, partial chunk fetches, sequential extents, and holes. Two corruption cases mark single-value and array-value records corrupted, then expect `vos_obj_fetch()` to return `-DER_CSUM`.

The helper tests are run in a second cmocka group. They construct minimal `evt_root`, `evt_context`, `evt_extent`, and `evt_entry` structures directly, avoiding VOS pool state for pure arithmetic and pointer-adjustment behavior.

## State And Persistence Behavior

Array checksum tests persist data and checksum blobs into VOS at epoch 1. Fetch state is observed through the internal bio descriptor and checksum list before `vos_fetch_end()`. Corruption tests mutate persistent bio addresses through iterator processing, then confirm the corruption marker survives iteration and changes fetch results.

## Dependencies And Integration Points

The file includes DAOS checksum types, `evt_priv.h`, and `vts_io.h`. It integrates with `setup_io()`/`teardown_io()` and touches VOS update/fetch begin/end, iterator processing, bio vectors, checksum list accessors, and EVT-private checksum helpers.

## Risks And Test Signals

Important risks include off-by-one checksum chunk alignment, missing checksums for partial fetches, holes incorrectly receiving checksums, and corrupted data still being readable. Passing signals are exact bio-vector prefix/suffix lengths, exact checksum byte equality, expected checksum-list counts, and `-DER_CSUM` after corruption marking.
