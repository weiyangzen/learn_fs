<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kcovtrace/kcovtrace.c -->
# sources/test-tools/syzkaller/tools/kcovtrace/kcovtrace.c

## Purpose

Exec wrapper that prints KCOV PCs for a child program.

## Important APIs, Types, and Functions

OS-specific KCOV device/ioctls, mmap, fork, execve, waitpid, atomic coverage reads.

## Control Flow

Initializes KCOV, forks, child enables coverage and execs program, parent waits, prints collected PCs, unmaps/closes.

## State and Persistence Behavior

Process-local shared coverage buffer; stdout only.

## Dependencies and Integration Points

Requires KCOV permissions on Linux/FreeBSD/NetBSD.

## Risks and Edge Cases

Simplistic for threads/grandchildren; NetBSD branch should be build-checked for variable consistency.

## Test Signals

Compile per OS and run known syscall program, then symbolize PCs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kcovtrace/kcovtrace.c -->
