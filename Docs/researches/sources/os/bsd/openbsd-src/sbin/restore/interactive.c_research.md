# File Research: sources/os/bsd/openbsd-src/sbin/restore/interactive.c

## Purpose

Interactive restore shell used by `restore -i`. It lets users browse the dump's virtual directory tree, mark files for extraction, unmark them, extract selected files, set modes, inspect dump metadata, and toggle verbosity/debugging.

## Command Loop

`runcmdshell()` initializes a glob context with alternate directory callbacks backed by `RST_DIR`, starts at canonical `/`, and loops reading commands. It handles `add`, `cd`, `delete`, `extract`, `help`/`?`, `ls`, `pwd`, `quit`/`xit`, `verbose`, `setmodes`, `what`, and `Debug`.

`add` resolves a path to an inode, optionally checks paths for restore-by-name mode, and calls `treescan(..., addfile)`. `delete` calls `treescan(..., deletefile)` for marked entries. `extract` runs `createfiles()`, `createlinks()`, `setdirmodes()`, and optional `checkrestore()`.

## Command Parsing

`getcmd()` reads from `terminal`, trims whitespace, splits the command and arguments, defaults missing arguments to the current directory, canonicalizes absolute and relative paths, and uses `glob()` with restore-backed directory/stat functions to expand patterns. Multi-argument commands are returned one path at a time across calls.

`copynext()` supports whitespace tokenization with backslash escaping and single/double quotes. `canon()` normalizes names to restore's `./...` form, collapses repeated/trailing slashes, and removes embedded `.` and `..` components.

## Listing And Globbing

`printlist()` resolves a path, skips files not present on the dump map unless debugging, and lists either a single file or directory contents. It marks selected entries with `*`, absent-debug entries with `^`, and appends type suffixes such as `/`, `@`, `=`, and `#`.

`mkentry()` converts a restore `struct direct` into display metadata. `formatf()` lays out sorted entries in columns and can include inode numbers in verbose mode. `glob_readdir()` and `glob_stat()` adapt restore's virtual directory tree to `glob(3)`.

## Interrupt Handling

`onintr()` longjmps back to the command shell during interactive commands, otherwise asks whether to continue and exits if declined. Source comments note signal/longjmp reentrancy and signal race concerns.

## Risks And Invariants

- Interactive globbing depends on `dumpmap` and the virtual directory file built by `extractdirs()`.
- `canon()` edits paths in fixed buffers; callers must provide `PATH_MAX`-sized destinations.
- The shell can leave partial glob state on interrupts, so `runcmdshell()` explicitly frees it after longjmp.
