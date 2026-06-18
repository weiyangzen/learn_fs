# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/cat_mail.c

`cat_mail()` handles local mailbox delivery. It unescapes the mailbox path, supports dry-run output modes, treats `/dev/null` as successful discard, opens the target folder with `openfolder()`, appends the message with mailbox `From ` escaping, writes a trailing newline, closes the folder, and logs delivery.

Failures to create or write the mail file are converted to `refuse()` calls. The final receiver name is derived from the last bang component for logging.
