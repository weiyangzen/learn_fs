# File Research: sources/os/plan9/9front/sys/src/cmd/size.c

Purpose: Prints text, data, bss, and total sizes for Plan 9 executable files.

Behavior:
- Uses `crackhdr` from `<mach.h>` to parse headers.
- Default file is `8.out` when no args are given.
- Output format: `<txt>t + <data>d + <bss>b = <total>\t<file>`.

Risks:
- Only handles files recognized by `crackhdr`.
- Exits `"error"` if any input fails.
