# sources/test-tools/cthon04/basic/subr.c

Purpose: shared support library for the basic Connectathon filesystem tests. It owns test-directory setup, recursive tree creation/removal, timing, error reporting, argument parsing helpers, success exit, and DOS/Win32 compatibility shims.

Important APIs/types/functions: exports Myname and Dflag, dirtree(), rmdirtree(), error(), starttime(), endtime(), testdir(), mtestdir(), getparm(), complete(), unix_chdir(), unix_mkdir(), and compatibility replacements for lstat(), gettimeofday(), statfs(), opendir()/readdir()/rewinddir()/closedir() on DOS/Win32. It depends on tests.h constants such as TESTDIR, CHMOD_RW, FNAME, DNAME, MAXPATHLEN, and DOSorWIN32.

Control flow: dirtree() recursively creates per-level files and directories, descending through unix_chdir() and returning via "..". rmdirtree() mirrors that traversal, unlinking known generated files before recursively removing generated directories. testdir() chooses an explicit directory, NFSTESTDIR, or TESTDIR, removes any old tree with rm -r/system or rmdir on WIN16, creates it, and chdirs into it. complete() prints the ok marker, restores any DOS/Win32 drive implied by Myname, and exits.

State and persistence: the helpers intentionally mutate the filesystem beneath the selected test directory. Timing is stored in static timeval globals ts/te. DOS/Win32 directory emulation uses global find state, one open directory at a time, and heap-allocated dirent lists that are not freed by closedir(). Dflag changes generated names to include level numbers.

Dependencies and integration points: all basic test programs link against this file or a prebuilt SUBR.OBJ. It bridges Unix syscalls and Microsoft C runtime calls, making the same tests usable from Unix makefiles, DOS makefiles, and Win32 NMAKE projects.

Risks: path construction uses fixed MAXPATHLEN buffers and sprintf; testdir() shells out to rm -r on a configurable path; directory emulation allocates a fixed 512-entry list; several compatibility routines assume DOS drive-letter paths and narrow 8.3 names. These are acceptable in the historical test harness but risky outside controlled test directories.

Test signals: successful callers print a per-test summary followed by "<program> ok.". Failures call error() with the current directory, preserve errno for perror(), and exit nonzero.
