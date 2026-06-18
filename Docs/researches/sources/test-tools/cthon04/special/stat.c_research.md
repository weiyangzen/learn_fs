# sources/test-tools/cthon04/special/stat.c

## Purpose
recursively stats every entry in a directory tree and reports metadata call rate.

## Important APIs, Types, and Functions
`main()`, recursive `statit()`, `starttime()`, `endtime()`, `telldir()`, `seekdir()`, `opendir()`, `readdir()`, and `lstat()`/`stat()` are key.

## Control Flow and State
`statit()` stats a path, returns for non-directories, opens directories, chdirs into them, stats children, recurses into child directories after saving a telldir cookie, reopens `.` and seeks back, then chdirs up.

## Persistence and Dependencies
state changes include process current working directory and `stats` counter; no files are modified. Dependencies: directory stream APIs, timing helpers from `../basic/subr.o`, and SVR3/directs conditionals.

## Integration Points, Risks, and Test Signals
Integration is directory metadata traversal performance. Risks are cwd mutation, telldir/seekdir portability, symlink behavior differences, and divide by zero if elapsed is zero. Signals are complete traversal and calls/sec output.
