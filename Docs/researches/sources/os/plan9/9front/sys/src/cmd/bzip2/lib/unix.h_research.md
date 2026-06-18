# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/unix.h

Purpose: Generic Unix platform include shim for bzip2.

Key points:
- Includes standard C/POSIX-ish headers: `stdio.h`, `stdlib.h`, `string.h`, `signal.h`, `math.h`, `errno.h`, and `ctype.h`.

Dependencies and interactions:
- Included by `os.h` when `BZ_UNIX` is selected.

Research notes:
- Minimal platform header. It provides declarations expected by the upstream bzip2 source.
