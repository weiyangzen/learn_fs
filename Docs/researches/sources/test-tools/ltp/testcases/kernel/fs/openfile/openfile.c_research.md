# sources/test-tools/ltp/testcases/kernel/fs/openfile/openfile.c

## Purpose

`openfile.c` stresses simultaneous opens of the same file by multiple pthreads. Each thread opens the file many times, waits at a condition-variable barrier, then closes all descriptors.

## Important APIs, Types, and Functions

Important pieces are control struct `cb` with mutex and condition variables, globals `numthreads`, `numfiles`, `debug`, `filename`, functions `setup`, `cleanup`, `threads`, and `close_files`. Options `-f`, `-t`, and `-d` control file count, thread count, and debug logging.

## Control Flow

`main` parses options, creates an LTP tempdir and a source file, caps counts to `MAXFILES` and `MAXTHREADS`, initializes pthread synchronization, locks the mutex, creates threads, waits until all threads report sleeping, broadcasts release, unlocks, reports pass, unlinks the file, and exits. Each thread opens `numfiles` handles before entering the barrier, then closes all handles after broadcast.

## State and Persistence Behavior

The shared persistent object is `FILETOOPEN`, removed by main or thread error paths. Per-thread `FILE *fd_list[MAXFILES]` arrays hold open streams until the barrier is released.

## Dependencies and Integration Points

Uses legacy LTP `test.h`, pthread mutex/condition APIs, `fopen`, `fclose`, `unlink`, and tempdir helpers.

## Risks and Edge Cases

The mode string `"rw"` is nonstandard; portable read/write update mode would be `"r+"` or `"w+"`. Threads are not joined, so late thread failures after broadcast are not collected by main. `sprintf` appends into a fixed `msg` buffer without output. Main reports `TPASS` once threads are awakened, not after verified thread completion.

## Test Signals

Intended pass signal is `TPASS "Threads are done reading"`. Practical failure signals include pthread creation/synchronization errors or `fopen` failures under descriptor pressure.
