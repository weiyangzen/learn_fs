# sources/user-network-fs/samba/source4/torture/ndr/string.c

## Purpose

`string.c` tests low-level NDR string push/pull behavior across ASCII, UTF-8, raw 8-bit, null-terminated, non-terminated, and charset-conversion scenarios. Unlike the other files in this group, it exercises generic NDR string primitives directly rather than generated RPC operation fixtures.

## Important APIs, Types, and Functions

- Includes `torture/ndr/ndr.h`, `torture/ndr/proto.h`, `../lib/util/dlinklist.h`, and `param/param.h`.
- Static string fixtures are `ascii`, `latin1`, and `utf8`, with byte arrays used to avoid source-encoding dependence.
- Flag aliases include `fl_ascii_null`, `fl_ascii_noterm`, `fl_utf8_null`, and `fl_raw8_null`.
- `test_ndr_push_string()` creates an `ndr_push`, sets string flags, calls `ndr_push_string()`, checks the expected `ndr_err_code`, output offset, data pointer, and byte comparison behavior.
- `test_ndr_pull_string()` creates a `DATA_BLOB` with `data_blob_string_const()`, initializes `ndr_pull`, calls `ndr_pull_string()`, and checks expected status/result comparison.
- `torture_ndr_string()` runs the push/pull matrix and temporarily changes `dos charset` between `ASCII`, `CP850`, and the saved original.
- `ndr_string_suite()` registers a simple test named `ndr_string` and sets a description.

## Control Flow

`torture_ndr_string()` saves the current DOS charset, runs push tests for valid ASCII, empty strings, UTF-8, raw8, Latin-1 raw8, and invalid ASCII conversions, then runs pull tests for valid ASCII/UTF-8/raw8 cases. It then forces `dos charset=ASCII` and expects Latin-1/UTF-8 under ASCII flags to fail with `NDR_ERR_CHARCNV`. Next it forces `dos charset=CP850` and expects success but string mismatch for the same malformed input combinations. Finally it restores the saved charset and reloads conversion tables.

The helper functions centralize allocation, flag setup, NDR primitive calls, expected-error checking, and comparison semantics. They free their temporary TALLOC contexts before returning.

## State and Persistence Behavior

There is no persistent state, but the test intentionally mutates `torture->lp_ctx` global parameters and reloads character conversion state. It preserves and restores the original `dos charset`, so state leakage risk is lower than in similar code that does not restore. Temporary NDR buffers are TALLOC-owned and freed in each helper.

## Dependencies and Integration Points

The file exercises the generic libndr string implementation and Samba's character conversion layer. It depends on loadparm mutation (`lpcfg_do_global_parameter()`), `reload_charcnv()`, NDR push/pull initialization helpers, and torture assertion macros. It provides regression coverage for callers throughout Samba that rely on `LIBNDR_FLAG_STR_*` semantics.

## Risks and Edge Cases

- Expected behavior depends on charset conversion tables and runtime loadparm behavior; environment or library changes can alter success/failure modes.
- The tests compare byte/string equality for simple cases but do not exhaustively validate UTF-16 or conformant-varying string encodings.
- `test_ndr_push_string()` uses `strlen()` to compute expected offsets, so it is intentionally scoped to single-byte output modes covered by the selected flags.
- A failure before restoration could leave the test context charset changed unless the torture framework tears it down.

## Test Signals

This file has strong unit-style signals: explicit expected `NDR_ERR_SUCCESS` and `NDR_ERR_CHARCNV`, output length checks, null/non-null output checks, and equality/mismatch checks under multiple string flag combinations. It is the most direct regression test in this group for character conversion behavior.
