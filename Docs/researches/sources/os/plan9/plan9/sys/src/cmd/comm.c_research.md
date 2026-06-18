# File Research: sources/os/plan9/plan9/sys/src/cmd/comm.c

Plan 9 implementation of `comm`, comparing two sorted text files and printing lines unique to file 1, unique to file 2, or common to both.

It parses `-1`, `-2`, and `-3` to suppress output columns, opens `-` as `/fd/0`, reads lines through `Biobuf`, compares bytewise, and drains the remaining file once the other reaches EOF. Lines are held in fixed 2048-byte buffers and are nul-terminated at newline or near buffer limit.

Dependencies are minimal: `<u.h>`, `<libc.h>`, and `<bio.h>`. The command assumes sorted input and does no locale collation.
