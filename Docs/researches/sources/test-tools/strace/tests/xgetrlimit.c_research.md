<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xgetrlimit.c -->
# sources/test-tools/strace/tests/xgetrlimit.c

## Purpose
Covers strace decoder coverage for `xgetrlimit`. Source comments/macros state: Check decoding of getrlimit/ugetrlimit syscall. space for 2 llu strings space for XLAT_STYLE_ABBREV decoding space for C style comments RLIM64_INFINITY XLAT_ABBREV RLIM_INFINITY XLAT_ABBREV %llu*1024 XLAT_ABBREV !XLAT_RAW RLIMIT_??? NR_GETRLIMIT Source read: 113 lines, 2654 bytes.

## Important APIs, Types, And Functions
includes/imports: <errno.h>, <stdint.h>, <stdio.h>, <sys/resource.h>, <unistd.h>, "xlat.h", "xlat/resources.h"; defines/undefs: none; C functions: sprint_rlim, main; syscall numbers/wrappers: NR_GETRLIMIT; struct types: xlat_data.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: NR_GETRLIMIT.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `xlat.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xgetrlimit.c -->
