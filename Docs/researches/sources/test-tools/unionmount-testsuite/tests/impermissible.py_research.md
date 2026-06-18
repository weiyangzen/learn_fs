# sources/test-tools/unionmount-testsuite/tests/impermissible.py

Purpose: verifies permission-denied behavior for non-root user operations against root-owned lower files and confirms privileged operations still work afterward.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`, `ctx.truncate`, `ctx.utimes`, and direct metadata checks.

Control flow: switches effective uid/gid through `as_bin` in context operations. Tests denied write/truncate/append/utime attempts expecting `EACCES`, checks contents/timestamps are unchanged, then performs the same operation as root and validates new content, size, or timestamps.

State and persistence: mutates `rootfile` content, size, and timestamps only in privileged parts. Permission-failed parts must not copy up or alter data.

Dependencies and integration: setup creates root-owned files; context handles `seteuid`/`setegid` around operations.

Risks: assumes uid/gid 1 exists and lacks write permission; timestamp equality can be coarse on some filesystems; terminal slash mode skips some size/time checks.

Test signals: validates permission checks occur before copy-up/data mutation.
