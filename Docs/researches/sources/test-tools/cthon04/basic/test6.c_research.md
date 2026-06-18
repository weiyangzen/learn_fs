# sources/test-tools/cthon04/basic/test6.c

Purpose: directory-read correctness test for readdir ordering/completeness across repeated rewinds while entries are removed.

Important APIs/types/functions: parses -h, -t, -f, -n, -i plus files/count/fname. Uses opendir(), rewinddir(), readdir(), closedir(), bitmap macros BIT/SETBIT/CLRBIT, unlink(), dirtree(), rmdirtree().

Control flow: validates count <= files and files <= MAXFILES, creates a flat file set, opens '.', then for each pass rewinds and checks that '.', '..', expected remaining files, and no removed files are reported. After each pass it unlinks the file matching the pass index.

State and persistence: mutates the directory during enumeration by deleting one generated file per pass, then runs rmdirtree(ignore=1) to clean remaining generated files.

Dependencies and integration points: uses native dirent on Unix and emulated dirent from subr.c/unixdos.h on DOS/Win32. -i supports running in a directory with unrelated entries.

Risks: bitmap limit caps files at 512; atoi accepts nonnumeric suffix prefixes weakly; filesystem-specific directory cache behavior can surface here.

Test signals: duplicate/missing/unexpected entries accumulate errors and fail immediately; success prints entries read and ok marker.
