# File Research: sources/os/plan9/plan9/sys/src/cmd/rm.c

Read status: complete, 102 lines.

This is the Plan 9 `rm` command. It supports `-r` recursive removal and `-f` ignore-errors behavior.

`main` attempts `remove` on each argument. If that fails and `-r` is set on a directory, `rmdir` recursively reads all entries, first tries to remove each child, then recurses into child directories that could not be removed directly, and finally removes the parent.

Errors are stored in `errbuf` and printed unless `-f` is active; the process exits with `errbuf`.

Filesystem relevance: direct filesystem mutation utility for file and recursive directory deletion.
