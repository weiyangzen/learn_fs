# sources/test-tools/ltp/testcases/kernel/fs/fs_di/fs_di

Purpose: shell-level filesystem data-integrity test. It writes generated data files into random-depth directory paths, copies them back, compares both directions, and optionally validates fragmented-file creation.

Important APIs/types/functions: `usage`, `end_testcase`, option parsing for `-d`, `-l`, `-s`, `-S`, `create_datafile`, `frag`, `cp`, `cmp`, `mkdir`, `chmod`, and LTP `tst_resm`.

Control flow: requires `-d` target directory, defaults to ten loops and a 30 MiB file, optionally chooses random sizes from 10-500 MiB, creates temp and test directories, then for each loop creates a data file, builds a random nested path, copies to the filesystem under test, compares after write, copies back, compares after read, and removes loop artifacts. If `-S` is given, it creates a half-partition-size file, runs `frag`, compares fragmented outputs, then cleans up.

State/persistence behavior: creates `$TCtmp`, `$TESTFS`, nested random directories, `testfile`, `testfile_copy`, and optional `frag1`/`frag2`; cleanup removes them when `CLEANUP=ON`.

Dependencies/integration: uses helper binaries built in the same directory and the legacy LTP shell library path. Intended for mounted filesystems supplied by the caller.

Risks/test signals: destructive cleanup removes `$TESTFS` and `$TMPBASE/*` paths, so `-d` must be isolated. The fragmented-file section contains a duplicated `retval` check and does not actually compare `frag2` before the second failure message. Pass/fail is entirely based on `cmp` and helper exit status.
