# sources/test-tools/unionmount-testsuite/tests/open-trunc.py

Purpose: baseline tests for opening existing regular files with `O_TRUNC`.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only+truncate empties the file. Write-only/read-write+truncate writes `q` then truncates again and writes `p`. Append+truncate behaves similarly, leaving only the post-truncate byte.

State and persistence: lower file is data-copied to upper and truncated; content becomes empty or one-byte values depending on writes.

Dependencies and integration: context open/truncate/write/read logic and lower file fixtures.

Risks: Linux allows `O_RDONLY|O_TRUNC` behavior that may be surprising; non-Linux semantics could differ.

Test signals: direct coverage for truncation-triggered copy-up and upper data mutation.
