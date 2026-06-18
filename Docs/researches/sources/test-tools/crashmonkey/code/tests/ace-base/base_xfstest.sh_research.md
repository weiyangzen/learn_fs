# sources/test-tools/crashmonkey/code/tests/ace-base/base_xfstest.sh

Purpose: shell template for generating xfstests-style crash-consistency tests using dm-flakey and common output normalization helpers.

Important APIs/functions: initializes xfstests environment, requires scratch device and dm-flakey, creates a 256 MiB scratch filesystem, defines `rename()`, `general_stat()`, `_dwrite_byte()`, `_mwrite_byte_and_msync()`, `check_consistency()`, and `clean_dir()`, then exits with "Silence is golden".

Control flow: setup validates filesystem/OS, formats scratch, initializes flakey target, defines helper functions, and currently performs no test cases before successful exit.

State and persistence behavior: intended generated tests would mutate `$SCRATCH_MNT`, drop/remount via flakey, and compare before/after stats. This template cleans temporary files and flakey state in a trap.

Dependencies: xfstests `common/rc`, `common/filter`, `common/dmflakey`, `$XFS_IO_PROG`, scratch device environment, and dm-flakey kernel target.

Risks: destructive scratch-device operations; helper `rename()` shadows a common command name; unquoted paths in places; `clean_dir()` uses `rm -rf $(find ...)`, which is whitespace-sensitive. As-is, it is a no-op success template rather than a behavioral test.

Test signals: generated tests should be silent on success and print before/after diffs on inconsistency.
