# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/nlisttst.c

Small standalone test harness for mailbox list matching code.

Key responsibilities:
- Includes `nlist.c` directly, supplies globals expected by the list implementation, and provides local `bye()`/`okmbox()` implementations.
- Runs `listboxes("list", ref, pat)` or `lsubboxes("lsub", ref, pat)` depending on `-l`.
- Prints the match count to stdout.

Filesystem relevance:
- Exercises the same mailbox name validation rules as `mbox.c`.
- Intended to test IMAP list pattern traversal over mailbox directories.

Notable quirks:
- Uses a Unicode arrow in output text.
- Duplicates the stoplist and `okmbox()` logic from production code.
