<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inode_of_sockfd.c -->
# sources/test-tools/strace/tests/inode_of_sockfd.c

## Purpose
Covers strace self-test coverage for `inode_of_sockfd`. Source comments describe: This file is part of strace test suite. Source read: 40 lines, 1014 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <limits.h>, <stdio.h>, <stdlib.h>, <string.h>, <unistd.h>; defines: none; C functions: inode_of_sockfd.

## Control Flow
Straight-line C test code built around helper macros and expected-output printing.

## State And Persistence Behavior
creates local sockets and socket option state only for the duration of the process.

## Dependencies And Integration Points
Depends on `tests.h`, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inode_of_sockfd.c -->
