# sources/sync-backup/unison/src/bytearray_stubs.c

Purpose: OCaml C stubs for copying between OCaml byte/string values and Bigarray-backed buffers.

Important APIs: `ml_blit_bytes_to_bigarray`, `ml_blit_string_to_bigarray`, and `ml_blit_bigarray_to_bytes`. `Array_data(a,i)` computes a byte pointer into `Caml_ba_data_val(a)` plus an OCaml integer offset.

Control flow: each stub extracts source/destination pointers from OCaml values, calls `memcpy` for `Long_val(l)` bytes, and returns unit. The string variant delegates to the bytes variant.

State/persistence: mutates only caller-provided OCaml bytes or bigarray memory; no external state.

Dependencies/integration: includes `caml/bigarray.h` and `caml/memory.h`. Used by OCaml code needing efficient buffer transfers without per-byte copying.

Risks: no bounds checks are performed in C; correctness depends on OCaml callers passing valid offsets/lengths. `memcpy` is unsafe for overlapping ranges, though intended use is between distinct storage classes.

Test signals: buffer roundtrip tests should verify exact copied contents and boundary behavior from the OCaml side.
