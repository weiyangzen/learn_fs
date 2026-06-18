# sources/test-tools/ltp/testcases/kernel/syscalls/exit/exit02.c

Purpose: Checks that exiting without an explicit `close()` still makes written file data readable by the parent.

Important APIs/types/functions: `SAFE_CREAT`, `SAFE_WRITE(SAFE_WRITE_ALL)`, `exit(0)`, `SAFE_FORK`, `tst_reap_children`, `SAFE_OPEN`, `SAFE_READ`, `memcmp`, and `.needs_tmpdir`.

Control flow: The child creates `test_file`, writes the filename string, and exits without closing. The parent reaps the child, reads the file, checks length and bytes, then unlinks it.

State and persistence behavior: Persistent tmpdir file content is the test state. It validates kernel close-on-exit/writeback behavior for an open fd.

Dependencies and integration points: Uses the modern LTP harness and isolated tmpdir.

Risks and test signals: The length failure message compares against the read buffer size in text, but the actual condition uses `sizeof(FNAME)`. Any missing implicit close/flush shows as short or wrong data.
