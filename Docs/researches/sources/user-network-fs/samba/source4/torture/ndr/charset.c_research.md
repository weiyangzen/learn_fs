# sources/user-network-fs/samba/source4/torture/ndr/charset.c

## Purpose
`charset.c` is a small NDR torture unit for charset push helpers. It verifies how `ndr_push_charset` and `ndr_push_charset_to_null` handle `NULL`, empty, and ordinary strings when encoding UTF-16LE scalar data into an NDR push context.

## Important APIs, types, and functions
- `test_ndr_push_charset(struct torture_context *tctx)` tests `ndr_push_charset(ndr, NDR_SCALARS, str, 256, 2, CH_UTF16LE)`.
- `test_ndr_push_charset_to_null(struct torture_context *tctx)` tests `ndr_push_charset_to_null` with the same bounds and charset.
- `ndr_charset_suite(TALLOC_CTX *ctx)` creates the `charset` suite, sets a descriptive label, and registers `push` and `push_to_null` simple tests.
- The fixture values are `NULL`, `""`, and `"test"`.

## Control flow
Each test allocates a zeroed `struct ndr_push` from the torture context and loops over the three string inputs. `test_ndr_push_charset` expects `NDR_ERR_INVALID_POINTER` only for the `NULL` input and `NDR_ERR_SUCCESS` for empty and non-empty strings. `test_ndr_push_charset_to_null` expects success for all three inputs, documenting that the `_to_null` variant tolerates `NULL`. Assertions use `torture_assert_ndr_err_equal` and `torture_assert_ndr_success`.

## State and persistence behavior
There is no persistent state. The only mutable object is the temporary `struct ndr_push` allocated under `tctx`. The same push context is reused across loop iterations, so the test also implicitly tolerates appending multiple charset encodings into a single push buffer.

## Dependencies and integration points
The file depends on `torture/ndr/ndr.h`, Samba's NDR push implementation, charset constant `CH_UTF16LE`, `ARRAY_SIZE`, and the torture assertion macros. It is linked into the overall NDR suite by `ndr.c` through `ndr_charset_suite(suite)`.

## Risks and edge cases
- The test checks return codes only; it does not inspect the encoded bytes, buffer length, terminator placement, or alignment.
- A single allocation of `struct ndr_push` is made without explicitly initializing all normal push fields beyond zeroing, so the test is narrowly tied to helper behavior that tolerates this setup.
- Only UTF-16LE with element size 2 and max length 256 is covered.
- Reusing one push context means a failure may depend on prior loop iterations if helper state handling changes.

## Test signals
The `push` subtest signals that the raw charset pusher rejects `NULL` and accepts `""`/`"test"`. The `push_to_null` subtest signals that the null-tolerant wrapper accepts all three inputs.
