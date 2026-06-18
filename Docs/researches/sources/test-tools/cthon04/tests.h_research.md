# sources/test-tools/cthon04/tests.h

## Purpose
`tests.h` is the shared portability and test helper contract for the Connectathon suite. It defines default test-tree dimensions, test directory paths, chmod masks, DOS/Windows compatibility includes, and prototypes for common timing and directory-tree helper routines.

## Important APIs, Types, and Functions
Important macros include `DOSorWIN32`, `ANSI`, `DNAME`, `FNAME`, `DDIRS`, `DLEVS`, `DFILS`, `TESTDIR`, `DCOUNT`, `CHMOD_MASK`, `CHMOD_NONE`, `CHMOD_RW`, `MAXPATHLEN`, `MAP_FAILED`, and `ARGS_()`. Declared helpers include `starttime()`, `endtime()`, `getparm()`, `dirtree()`, `rmdirtree()`, `testdir()`, `mtestdir()`, `complete()`, optional `strerror()`, `unix_chdir()`, and `error()`.

## Control Flow and State
There is no runtime control flow in the header. Preprocessor branches select Unix defaults or DOS/Win defaults, include `unixdos.h` where needed, and remap stdio streams for DOS/Windows redirected output.

## Persistence and Dependencies
No state is persisted directly, but the header declares external `Myname` and fixes constants used by many tests to create files, directories, and chmod modes. Dependencies: system errno headers, Windows/DOS headers when selected, `unixdos.h`, and helper implementations in `basic/subr.c`.

## Integration Points, Risks, and Test Signals
Integration is broad across basic, general, and special Cthon tests. Risks include global macro pollution, old K&R prototype support, path-length differences, a Unix default `TESTDIR` of `/mnt/nfstestdir`, and DOS stdio macro remapping. Test signals are successful cross-platform builds and consistent helper signatures for all suites.
