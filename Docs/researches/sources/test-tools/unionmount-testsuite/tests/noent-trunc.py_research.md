# sources/test-tools/unionmount-testsuite/tests/noent-trunc.py

Purpose: verifies `O_TRUNC` without `O_CREAT` still fails on absent files.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only+truncate, write-only+truncate, append+truncate, read-write+truncate, and append/read-write+truncate are attempted twice and must return `ENOENT`.

State and persistence: no files should be created; shadow dentry remains negative.

Dependencies and integration: exercises context open flag composition and missing path handling.

Risks: filesystems must not treat truncate as implicit create; terminal slash handling can affect errno.

Test signals: catches accidental upper creation or wrong errno on truncating absent paths.
