# File Research: sources/os/plan9/9front/sys/src/cmd/auth/status

Rc script that prints status for a user’s Plan 9 key and network key.

Important behavior:
- Requires exactly one user argument.
- For `/mnt/keys/<user>`, reads `status` and `expire`, formats expiration, reports whether the Plan 9 key is expired or active, and prints the last matching line from `/adm/keys.who`.
- For `/mnt/netkeys/<user>`, performs the same status/expiration reporting, runs `auth/printnetkey <user>` for non-expired network keys, and prints the last matching line from `/adm/netkeys.who`.

Filesystem relevance:
- Reads key status through mounted key filesystems and administrative who files.
