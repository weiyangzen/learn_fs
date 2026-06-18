# sources/test-tools/unionmount-testsuite/tests/open-creat-trunc.py

Purpose: tests existing-file open behavior with `O_CREAT|O_TRUNC`.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: read-only+truncate empties the file. Write-only/read-write truncates then writes `q`, then repeats and writes `p`. Append variants with truncate also produce exactly the newly written byte after each open. Readbacks validate content.

State and persistence: lower file is copied up with data and truncated/overwritten in upper layer.

Dependencies and integration: exercises data copy-up, truncation, create-no-op on existing files, and readback checks.

Risks: truncation through overlayfs must happen on upper copy; content expectations are sensitive to `O_APPEND|O_TRUNC` ordering.

Test signals: key data-copy-up/truncate coverage.
