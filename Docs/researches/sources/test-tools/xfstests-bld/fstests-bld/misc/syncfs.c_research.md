# sources/test-tools/xfstests-bld/fstests-bld/misc/syncfs.c

## Purpose

`sources/test-tools/xfstests-bld/fstests-bld/misc/syncfs.c` is a minimal command-line wrapper around the Linux `syncfs(2)` system call. Given a path to a file or directory, it opens that path and asks the kernel to flush all dirty data and metadata for the filesystem containing the opened file descriptor. This gives shell-based filesystem tests a precise way to issue filesystem-scoped syncs without syncing every mounted filesystem.

The source was read as a complete 40-line C file for this report.

## Important APIs, Types, and Functions

The file defines `_GNU_SOURCE` so glibc exposes the `syncfs` prototype from `<unistd.h>`. `progname` holds `argv[0]` for usage output. `usage(void)` prints `Usage: <progname> <file>` and exits 1. `main(int argc, char **argv)` validates that exactly one path argument was supplied, opens it read-only with `open(argv[1], O_RDONLY)`, reports open failures with `perror(argv[1])`, calls `syncfs(fd)`, reports sync failures with `perror("syncfs")`, and returns 0 on success.

## Control Flow

The control flow is deliberately linear. Argument validation happens first; incorrect invocation never attempts filesystem work. A successful `open` anchors the operation to the target file's mount. A successful `syncfs` completes the requested flush and the program exits 0. There is no retry logic, option parsing, directory traversal, or fallback to global `sync(2)`.

## State and Persistence Behavior

This helper does not maintain application state or write files directly. Its external side effect is forcing writeback for dirty data and metadata associated with the filesystem that owns the opened file descriptor. The file descriptor is not explicitly closed, relying on process exit for cleanup. It does not change the target file's contents, permissions, or timestamps except for any effects the kernel filesystem implementation associates with completing pending writeback.

## Dependencies and Integration Points

The program depends on Linux or another libc/kernel combination that provides `syncfs`, plus ordinary POSIX file APIs from `<fcntl.h>` and `<unistd.h>`. It integrates with xfstests-bld shell tests that need to flush a specific mounted test filesystem before crash simulation, remount, snapshot comparison, or durability assertions.

## Risks and Edge Cases

`syncfs` is Linux-specific and gated by `_GNU_SOURCE`, so portability to non-Linux targets is intentionally limited. Opening the path read-only can fail for permission, missing file, stale mount, or path resolution errors; the program reports the path but does not add contextual mount information. It does not use `O_DIRECTORY`, so both files and directories work, but symlinks are followed by default. The helper exits immediately after a failed `syncfs` without closing the descriptor, which is acceptable for a short-lived utility but not a reusable library pattern. Tests that need to distinguish writeback errors from earlier failed writes must remember that `syncfs` can surface delayed filesystem errors.

## Test Signals

Useful signals include a compile test on the intended Linux toolchain; invoking without arguments and with too many arguments to confirm usage failure; invoking on an existing file and directory on a writable test filesystem; invoking on a missing path to confirm the path-specific `perror`; and fault-injection or special-device tests that can make `syncfs` return an error and confirm the utility exits nonzero.
