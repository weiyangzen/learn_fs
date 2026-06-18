# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/filter.c

`upas/filter` is a small delivery helper that reads a message, optionally matches sender/header/body regex rules, rewrites the target mailbox path, and delivers via `cat_mail()`. Flags select dry-run, header matching, and body matching.

It strips a leading local system from the parsed sender before matching. Each regexp/replacement pair is applied in order; first matching sender or selected message region rewrites the mailbox filename using `regsub()`.

The local `refuse()` exits immediately after printing the error, making this utility a simple command-line filter rather than a full bounce-capable mailer.
