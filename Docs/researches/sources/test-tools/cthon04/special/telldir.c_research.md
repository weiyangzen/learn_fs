# sources/test-tools/cthon04/special/telldir.c

## Purpose
validates that `telldir()` cookies can be fed back to `seekdir()` to resume at the same directory entry.

## Important APIs, Types, and Functions
`file_info_t` records `inuse`, `cookie`, and remaining file count. Important functions are `alloc_file_info()`, `make_files()`, `walk_dir()`, `save_file_info()`, `check_file_info()`, `verify()`, and `cleanup()`.

## Control Flow and State
The program creates `telldir-test` with numbered files, opens it, walks entries while saving each pre-read cookie, then for each saved cookie seeks back and verifies the expected first file and remaining entry count.

## Persistence and Dependencies
persistent state is the scratch directory and `file_info` array; cleanup shells out `rm -rf telldir-test`. Dependencies: POSIX directory cookies, `calloc`, `creat`, `mkdir`, and `../tests.h` for `MAXPATHLEN`/prototypes.

## Integration Points, Risks, and Test Signals
Integration is directory cookie correctness testing. Risks are relying on directory order matching numeric names, unsafe `system("rm -rf")`, ignoring `.`/`..` while counting, and undefined behavior if filenames are unexpected. Signals are no missing info, no premature EOF, and zero exit.
