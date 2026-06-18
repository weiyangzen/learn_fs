# sources/test-tools/unionmount-testsuite/tests/truncate.py

Purpose: tests explicit truncate sizes on existing regular files and validates resulting file size and content prefixes.

Important APIs and functions: one `subtest_1(ctx)` uses `ctx.reg_file()`, `ctx.get_file_size()`, `ctx.truncate()`, `ctx.open_file()`, `ctx.incr_filenr()`, and `TestError`.

Control flow: builds a 29-byte expected key by padding `:xxx:yyy:zzz` with NULs, then loops sizes 0..28. For non-trailing-slash mode it validates initial size, truncates, checks post size, and reads the expected prefix. In trailing-slash mode it expects `ENOTDIR`.

State and persistence: each loop uses a fixture file and advances the file number to avoid repeated truncation of one path. Truncation changes file length and content visibility.

Dependencies and integration: depends on context size and truncate helpers, and on `TestError` being available from harness imports.

Risks: binary NUL content in expected reads requires the harness to compare exact strings. Initial file size is assumed to be 12.

Test signals: exact post-truncate size and prefix data for every tested length, or expected `ENOTDIR` in trailing slash mode.
