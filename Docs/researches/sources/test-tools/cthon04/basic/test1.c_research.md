# sources/test-tools/cthon04/basic/test1.c

Purpose: basic create benchmark and correctness test for file/directory creation on the mounted filesystem.

Important APIs/types/functions: parses -h, -t, -f, -n plus optional levels/files/dirs/fname/dname. Uses getparm(), testdir()/mtestdir(), dirtree(), starttime(), endtime(), complete(), creat(), mkdir/chdir through subr.c.

Control flow: defaults to DLEVS/DFILS/DDIRS and FNAME/DNAME, validates that multi-level trees have at least one subdirectory per level, optionally shrinks to a 2x2 functionality run, enters the test directory, then delegates recursive creation to dirtree().

State and persistence: creates a tree under NFSTESTDIR or TESTDIR and intentionally leaves it in place for removal or later tests. Totals are maintained in local counters passed by pointer to dirtree().

Dependencies and integration points: compiled by Unix, DOS, and Win32 project files with subr.c; hidden -s mode suppresses non-error output for test2's setup path.

Risks: generated names use fixed buffers in subr.c; large levels/files/dirs values can create very large trees; -n assumes the directory already exists.

Test signals: reports created file/directory counts and optional elapsed time, then complete() prints the ok marker.
