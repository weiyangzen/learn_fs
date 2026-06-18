# File Research: sources/os/plan9/plan9/sys/src/cmd/diff/main.c

Front end and dispatcher for Plan 9 `diff`.

It parses options `-e`, `-f`, `-n`, `-c`, `-a`, `-w`, `-b`, `-r`, `-m`, and `-h`. It initializes buffered stdout, validates argument counts, detects multi-file/directory mode, and loops over all source operands against the final target operand.

`statfile` normalizes operands. It handles `-` stdin by copying to a temp file, and copies non-regular/non-directory inputs to temp files so the regular diff path can read them repeatedly. `mktmpfile` creates `/tmp/diff...` files and records them for cleanup. `diff` dispatches directory-vs-directory to `diffdir`, regular-vs-regular to `diffreg`, and file-vs-directory by appending the basename to the directory path.

`panic`, `done`, and `rmtmpfiles` handle errors, exit statuses, and temp cleanup. `emalloc`/`erealloc` are fatal allocation wrappers.

Integration points: owns global flags declared in `diff.h` and coordinates `diffdir.c`, `diffreg.c`, and `diffio.c`.

Risks and notes: temp names use `mktemp`, consistent with old Plan 9 style but inherently race-prone by modern standards. Errors in multi-file mode can be nonfatal through status `0` panics.
