# sources/storage-engines/wiredtiger/test/packing/int4bpack-test.c

## Purpose
This C test validates WiredTiger's 4-bit/nibble-oriented positive integer array packing implementation and signed zigzag helpers. It combines human-readable encoding dumps, boundary checks, buffer-size error checks, partial decoding, and randomized fuzzing.

## Important APIs, Types, and Functions
The file includes `test_util.h` and exercises internal APIs `__wt_4b_pack_array`, `__wt_4b_unpack_array`, `__wt_4b_size_array`, `__4b_unpack_init`, `__4b_unpack_posint_ctx`, `__wt_encode_signed_as_positive`, and `__wt_decode_positive_as_signed`. Scenario functions include `test_positive_integers`, `test_signed_integers`, `test_pairs_of_integers`, `test_small_int_arrays`, `test_bigger_int_arrays`, `test_extreme_values`, `test_alignment_boundaries`, `test_exact_fit_and_enomem`, `test_truncated_and_overcount_decode`, `test_partial_decode_resume`, and `test_random_fuzz`.

## Control Flow
`main` initializes the WT library, runs deterministic coverage first, then fuzzes positive and signed arrays. Round-trip helpers encode values into fixed buffers, assert encoded length equals `__wt_4b_size_array`, decode through pointer-advancing APIs, verify full consumption, print encoded bytes/bits, and compare decoded values. Error tests intentionally use too-small buffers or truncated inputs and assert `ENOMEM` or `EINVAL`.

## State, Persistence, and Integration
The test is in-memory only. Its state is local buffers, pointer cursors, deterministic arrays, and a seeded `WT_RAND_STATE`. It integrates directly with internal packing code and test utility allocation/assertion/random helpers. Printed output documents the byte and bit representation for manual inspection, but correctness relies on assertions.

## Risks and Test Signals
Risk areas include nibble alignment flips across element boundaries, boundary values near encoding length changes, UINT64 and INT64 extremes, exact-fit buffer handling, truncated decode validation, and resumable context decoding. The fuzz loops broaden coverage across random lengths and values. Strong signals are pointer consumption checks, expected packed-size checks, explicit error-code assertions, and deterministic edge-case arrays.
