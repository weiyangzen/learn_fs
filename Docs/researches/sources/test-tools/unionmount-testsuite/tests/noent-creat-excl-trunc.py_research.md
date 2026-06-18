# sources/test-tools/unionmount-testsuite/tests/noent-creat-excl-trunc.py

Purpose: verifies creation of missing files with `O_CREAT|O_EXCL|O_TRUNC` under different access modes.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: each subtest opens a missing path with create/exclusive/truncate and read-only, write-only, append, read-write, or append/read-write. First open creates an empty or one-byte file; second exclusive open expects `EEXIST`; final read confirms content.

State and persistence: creates one new upper file per subtest and writes `q` where applicable.

Dependencies and integration: depends on `context.open_file` create/exclusive/truncate state updates and content checking.

Risks: terminal slash mode can convert missing-file creation to directory-related errors through context overrides.

Test signals: validates exclusive creation and no unintended truncation after `EEXIST`.
