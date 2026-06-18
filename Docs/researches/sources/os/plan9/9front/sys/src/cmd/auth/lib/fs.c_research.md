# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/fs.c

Static description table for mounted auth key filesystems.

Key contents:
- Defines `fs[Plan9]` as `/mnt/keys`, label `plan 9 key`, bio file `/adm/keys.who`.
- Defines `fs[Securenet]` as `/mnt/netkeys`, label `network access key`, bio file `/adm/netkeys.who`.

Role:
- Shared by account/key management tools to address Plan 9 and Securenet databases consistently.
