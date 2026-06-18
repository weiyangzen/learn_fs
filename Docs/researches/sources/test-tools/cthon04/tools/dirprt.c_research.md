# sources/test-tools/cthon04/tools/dirprt.c

## Purpose
prints directory entries using standard `opendir()`/`readdir()` plus `telldir()` cookies for easier inspection than `dirdmp`.

## Important APIs, Types, and Functions
`main()`, `print()`, and `my_opendir()` are key; output fields vary between SVR/Linux `d_ino` and BSD-style `d_fileno`/`d_namlen`.

## Control Flow and State
For each argument, it stats the path, verifies it is a directory, opens it, iterates entries, prints current `telldir()` and dirent metadata, then closes.

## Persistence and Dependencies
no persistent state beyond directory stream position. Dependencies: dirent APIs, stat headers, and platform `use_directs`/AIX conditionals.

## Integration Points, Risks, and Test Signals
Integration is a portable directory-cookie/display tool. Risks are AIX unsupported path, platform-specific dirent fields, and no usage diagnostics for missing args. Signals are per-entry printed cookies and metadata.
