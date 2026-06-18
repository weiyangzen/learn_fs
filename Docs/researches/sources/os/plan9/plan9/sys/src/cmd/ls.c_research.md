# File Research: sources/os/plan9/plan9/sys/src/cmd/ls.c

Read fully: 326 lines, 5723 bytes. SHA-256 prefix: `2af09045bde4ef0e`.

This is Plan 9 `ls`. It supports flags for directory-as-file, long output, muid, no sort, path prefix, qid/version, reverse, size blocks, time sort, temp marker, access time, file suffixes, and unquoted names.

`ls()` stats each argument, reads directories when needed, stores `Dir` pointers plus optional prefixes, and calls `output()`. `output()` sorts unless disabled, computes column widths, and formats each entry. `format()` emits selected fields using Plan 9 formatters. `compar()` sorts by name/prefix or time and applies reverse. `asciitime()` chooses recent vs old timestamp display. `xcleanname()` compresses slashes and strips trailing slashes.

Risk notes: modifies argument strings in place when splitting path prefixes. Directory buffers are resized with `realloc()` and entries from `dirreadall()` are retained until output flush.
