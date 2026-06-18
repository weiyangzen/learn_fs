# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/status

Rc script that reports Plan 9 and network key status for a user. It checks `/mnt/keys/<user>` and `/mnt/netkeys/<user>`, reads `status` and `expire`, formats expiration with `date`, and prints metadata from `/adm/keys.who` or `/adm/netkeys.who`.

For network keys it also runs `auth/printnetkey`.
