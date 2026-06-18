# sources/test-tools/unionmount-testsuite/tests/symx-creat-excl.py

Purpose: checks exclusive create through a dangling symlink. Because the symlink's target is absent, `O_CREAT|O_EXCL` should fail with `EEXIST` for the symlink itself.

Important APIs and functions: five subtests use `ctx.pointless()` for a broken symlink, `ctx.no_file()` for the absent target, and `ctx.open_file()` with `crt=1, ex=1`.

Control flow: each subtest attempts an exclusive create through the dangling symlink under different access modes and expects `EEXIST`.

State and persistence: no new target file should be created and the dangling symlink should remain in place.

Dependencies and integration: relies on Linux `O_EXCL` symlink behavior and harness errno checking.

Risks: filesystems or wrappers that follow dangling symlinks before applying exclusive-create rules could report different errno or create the target.

Test signals: every open returns `EEXIST`; no follow-up reads are needed because the operation must not create data.
