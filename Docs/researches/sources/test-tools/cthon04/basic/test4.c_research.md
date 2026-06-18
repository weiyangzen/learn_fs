# sources/test-tools/cthon04/basic/test4.c

Purpose: setattr/getattr/lookup correctness and timing test over a flat set of files.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname. Uses dirtree() to create files, chmod(), stat(), CHMOD_NONE, CHMOD_RW, CHMOD_MASK, and timing helpers.

Control flow: prepares the test directory, creates one level of files, then for each pass and file toggles permissions to the no-access mask, verifies stat mode, toggles to read/write, and verifies again.

State and persistence: creates files under the test directory and does not remove them at the end, leaving cleanup to later tests or external harness logic.

Dependencies and integration points: depends on subr.c and tests.h for mode masks that differ between Unix and DOS/Win32.

Risks: no cleanup in this file; chmod semantics vary on Windows and network filesystems; exits with status 0 on some chmod failures, which can weaken failure detection.

Test signals: reports chmod/stat operation count and exits via complete() after all mode checks pass.
