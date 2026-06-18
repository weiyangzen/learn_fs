# sources/sync-backup/rsync/getfsdev.c

## Purpose

`getfsdev.c` is a tiny diagnostic/helper program that prints the filesystem device major/minor pair for each pathname argument. It is built against rsync portability definitions so it can use the same `STRUCT_STAT` and optional `stat64()` choice as the main program.

## Important APIs, Types, And Functions

The only function is `main(int argc, char *argv[])`. It declares `STRUCT_STAT st`, chooses `stat64()` when `USE_STAT64_FUNCS` is configured and `stat()` otherwise, then prints `major(st.st_dev)` and `minor(st.st_dev)` as `major/minor`.

## Control Flow

The program iterates over command-line paths with `while (--argc > 0)`, stats each path, exits with status 1 on the first stat failure, prints one line per successful path, and exits 0 after all paths are processed.

## State, Dependencies, And Integration

There is no persistent state. It depends on `rsync.h` for `STRUCT_STAT`, feature macros, standard headers, and device-number macros. It is likely used by build tests or developer diagnostics around device-number portability and `--one-file-system` behavior.

## Risks

The program casts major/minor values to `long`, which is appropriate for diagnostics but not a stable machine-readable ABI on exotic platforms. It stops at the first failed path and prints a generic error without `strerror(errno)`.

## Test Signals

Run it against regular files, directories, mount points, missing paths, and platforms that enable `USE_STAT64_FUNCS`. Expected output is one `major/minor` line per existing input and nonzero exit on failure.
