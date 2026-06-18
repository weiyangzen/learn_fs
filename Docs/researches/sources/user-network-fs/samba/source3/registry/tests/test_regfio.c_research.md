<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/tests/test_regfio.c -->
# sources/user-network-fs/samba/source3/registry/tests/test_regfio.c

Purpose: Cmocka unit tests for basic `regfio` behavior and corruption hardening.

Important APIs, types, and functions: Defines `struct test_ctx`, setup/teardown helpers, `open_testfile()`, `test_regfio_open_new_file()`, `test_regfio_corrupt_hbin()`, `test_regfio_corrupt_lf_subkeys()`, and `main()`.

Control flow: Tests allocate a talloc test context, optionally create a temporary file with `mkstemp()`, open registry fixtures under `SRCDIR/testdata/samba3`, and close/unlink/free in teardown. The new-file test opens a truncating writable hive, asserts no root exists yet, creates empty subkey/value containers, writes the root key, and verifies its NK header and root-key type. Corrupt fixture tests assert corrupt HBIN input yields no root and that corrupt LF subkey data does not crash while iterating.

State and persistence behavior: Temporary files are created under `/tmp/regfio.XXXXXX` and removed during teardown. `REGF_FILE` handles are stored in the context and closed if present. Fixture files are read-only.

Dependencies and integration points: Depends on cmocka, Samba talloc and file utilities, `registry/regfio.h`, and fixture data in `testdata/samba3`. It is the direct test signal for `regfio.c`.

Risks: The tests are intentionally narrow and mostly assert non-crash behavior. They do not validate value serialization, security descriptors, checksum handling, cross-HBIN records, or full round-trip correctness. The temporary path is hard-coded to `/tmp`.

Test signals: Current signals are successful new hive initialization/root write, graceful failure on corrupt HBIN, and safe iteration over corrupt LF subkey records. Expanding this file would be the natural place for round-trip and fuzz-regression cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/tests/test_regfio.c -->
