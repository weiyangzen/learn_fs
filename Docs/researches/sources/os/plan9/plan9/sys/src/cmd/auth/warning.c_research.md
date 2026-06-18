# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/warning.c

Sends expiration warning mail for Plan 9 and/or Securenet key databases. It scans mounted key directories, checks `expire` and `warnings`, sends one warning about two weeks before expiration and another about one week before, then updates the warning counter.

Recipients are extracted from `<...>` addresses in the associated `who` file; if none are found, it mails the user directly and also mails `netkeys`. It forks `/bin/upas/send` in a `none` namespace and can include `/adm/warn.<keysdir>` message text.

Supports `-p`, `-n`, and debug mode.
