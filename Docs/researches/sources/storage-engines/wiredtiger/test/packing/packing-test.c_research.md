# sources/storage-engines/wiredtiger/test/packing/packing-test.c

Purpose: small C smoke test for WiredTiger's internal struct packing helpers. It exercises valid and invalid packing format strings and prints the resulting byte sequences for human/debug visibility.

Important APIs and control flow: `check()` first calls `__wt_struct_sizev` to compute the packed length for a varargs format, validates that it fits a 200-byte local buffer, then calls `__wt_struct_packv` and prints bytes as hexadecimal. `main()` initializes test utility state with `testutil_set_progname()` and `__wt_library_init()`, then checks `iii`, `3i`, `iS`, `s`, and `.s` formats and asserts `>s`, `<s`, and `@s` return `EINVAL`.

State and persistence behavior: the program creates no WiredTiger home and writes no database state. State is limited to stack buffers, varargs traversal, and stdout output.

Dependencies and integration points: depends on `test_util.h`, internal `__wt_struct_sizev`/`__wt_struct_packv`, `WT_TRET`, `WT_RET`, and the library initialization path needed for internal data references. It is run by the packing smoke script.

Risks: it tests only a narrow set of formats and relies on internal WiredTiger functions, so ABI/config changes can break it outside public API compatibility. The varargs list must be restarted between size and pack calls, which the test handles explicitly.

Test signals: successful process exit validates valid formats and invalid-format rejection; printed hex output is useful for diagnosing packing layout drift.
