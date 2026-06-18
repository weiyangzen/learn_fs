# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/25

Purpose: Short OpenBSD kqueue fixture for a queued-state invariant. Expected title is `kqueue: knote !QUEUED`.

Important parser APIs and patterns: handled by the same `panic: (kqueue|knote).* ([a-z]+ .*)` formatter as other kqueue/knote fixtures. The source line `knote_enqueue:1276` and pointer fields should not appear in the deduplicated title.

Control flow: the panic reports `knote_enqueue:1276`, drops into DDB, and shows a compact stack: `db_enter`, `panic`, `kqueue_do_check`, `knote_enqueue`, `kqueue_register`, `sys_kevent`, `syscall`, `Xsyscall`. Unlike larger fixtures, it stops after the OpenBSD bug-report guidance, so it tests minimal but complete report extraction.

State and persistence: static testdata only. It captures two executor threads on different CPUs to preserve concurrency context for the stack.

Dependencies and integration: validates OpenBSD panic recognition and stable title formatting for a `knote_` function, not only `kqueue_` functions.

Risks: because the file is only 19 lines, an overly strict parser expecting DDB commands after the guidance block could mark it incomplete. Regex changes could include source line numbers or addresses in the title.

Test signals: exact title `kqueue: knote !QUEUED`; stack should include `knote_enqueue` and `kqueue_register`.
