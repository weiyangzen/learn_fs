# File Research: sources/os/plan9/9front/sys/src/cmd/auth/warning.c

Key-expiration warning mailer for Plan 9 and securenet auth filesystems.

Important behavior:
- Options select Plan 9 keys (`-p`), securenet keys (`-n`), or both by default; `-d` debug mode.
- `dodir()` scans a key directory from `authcmdlib.h` `fs[]`.
- `douser()` reads `<user>/expire` and `<user>/warnings`, sends one warning two weeks before expiry and another one week before expiry, then updates warnings count.
- Recipients come from matching lines in the configured who file, extracting addresses inside `<...>`. If none are found, mails the user directly.
- Always also mails `netkeys`.
- `mail()` forks `/bin/upas/send -r <recipient>`, writes a warning body through a pipe, and appends `/adm/warn.<keydirname>` if present.
- Child uses `newns("none", 0)` and sets `upasname=netkeys`.

Filesystem relevance:
- Traverses mounted key directories, reads numeric control files, updates warning counters, and reads admin warning templates.
