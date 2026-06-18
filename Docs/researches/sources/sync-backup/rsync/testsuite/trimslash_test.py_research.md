# sources/sync-backup/rsync/testsuite/trimslash_test.py

Purpose: unit-style test for the `trimslash` helper, which calls `trim_trailing_slashes()` on each argument and prints the result.

Important APIs and flow: constructs six path inputs covering no trailing slash, one/many trailing slashes, double leading slash, all slashes, and spaces/interior triple slashes. It runs `TOOLDIR/trimslash` with all inputs, fails on non-zero exit, and compares stdout exactly to the expected newline-terminated output.

State and persistence: no filesystem mutation. The only state is subprocess stdout/stderr.

Dependencies and integration: connects to `trimslash.c` and the shared path utility implementation from rsync core. Risks are platform path semantics if `trim_trailing_slashes()` intentionally treats double leading slashes differently, but the expected output documents current behavior. Test signal is exact stdout equality.
