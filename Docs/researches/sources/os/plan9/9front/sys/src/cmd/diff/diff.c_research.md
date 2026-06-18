# File Research: sources/os/plan9/9front/sys/src/cmd/diff/diff.c

Main entry point for Plan 9 `diff`.

Key elements:
- Parses output mode flags `-e`, `-f`, `-n`, `-c`, `-a`, `-u`.
- Parses whitespace flags `-w` and `-b`, recursive `-r`, and merge/directory behavior `-m`.
- Validates argument count and target path.
- If multiple source files are supplied, requires the final argument to be a directory and enables merge-style path behavior.
- If two directories are compared, enables directory mode.
- Calls `diff(argv[i], target, 0)` for each source.
- Exits with Plan 9 status strings: empty for no changes, `some` for differences, `error` otherwise.

Dependencies:
- Uses globals and functions declared in `diff.h`.
- Directory and regular-file behavior is implemented in other `diff` module files.

Research notes:
- This file is only CLI dispatch; algorithmic diff logic is elsewhere.
