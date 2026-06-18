# File Research: sources/os/plan9/9front/sys/src/cmd/aux/lines.c

Role: Simple line-preserving file concatenation utility.

Behavior:
- With no file arguments, reads stdin; otherwise opens and reads each named file.
- Uses `Brdline` to read newline-delimited lines and writes each complete line to stdout.
- Fails on output write errors or input open failures.

Limitation:
- It only writes data returned by `Brdline`, so a final unterminated partial line is not emitted.
