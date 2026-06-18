# sources/test-tools/unionmount-testsuite/tests/open-creat-excl-trunc.py

Purpose: tests opening existing lower files with `O_CREAT|O_EXCL|O_TRUNC`.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: all read/write/append variants expect `EEXIST` because the file exists. Each subtest then opens read-only and verifies original `:xxx:yyy:zzz` content remains.

State and persistence: no intended mutation; truncate must not occur after exclusive failure.

Dependencies and integration: lower regular file fixtures and context open/exclusive handling.

Risks: error precedence with terminal slash may differ if path is treated as directory-like.

Test signals: validates `O_EXCL` prevents copy-up/truncation of existing lower files.
