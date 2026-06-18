# sources/test-tools/cthon04/special/stat2.c

## Purpose
creates a directory full of numbered files and repeatedly stats them to measure metadata performance under a fixed working set.

## Important APIs, Types, and Functions
`main()` uses `mkdir()`, `chdir()`, `creat()`, `stat()`, `starttime()`, `endtime()`, `files`, `count`, and `stats`.

## Control Flow and State
It creates/chdirs into the supplied directory, creates `files` numbered files, times `count` passes over all file names with `stat()`, and prints aggregate calls/sec.

## Persistence and Dependencies
persistent state is the created directory and numbered files; no cleanup is performed. Dependencies: POSIX directory/file creation, stat, and timing helpers.

## Integration Points, Risks, and Test Signals
Integration is repeated metadata-cache testing. Risks are destructive name reuse, no cleanup, no close-error checking, and cwd mutation. Signal is all stat calls succeed and timing output matches `files * count`.
