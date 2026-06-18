# File Research: sources/os/plan9/9front/sys/src/cmd/rm.c

`rm.c` is Plan 9's `rm` command with `-f` and `-r`. The main loop first tries `remove` directly and, if recursive mode is enabled and the target is a directory, calls `rmdir`.

`rmdir` opens a non-empty directory, reads all entries with `dirreadall`, tries to remove each child directly, records remaining child directories, recursively removes those directories, and finally removes the original directory.

Errors are reported through `err`, which respects `ignerr` from `-f` and stores the last system error in `errbuf`. The program exits with `errbuf`, so a successful run exits cleanly and failures carry the last error string.

The implementation avoids recursing into entries that were removed successfully by rewriting their `qid.type` to `QTFILE`, then only recursing through entries still marked `QTDIR`.
