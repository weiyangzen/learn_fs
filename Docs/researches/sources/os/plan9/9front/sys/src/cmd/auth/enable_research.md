# File Research: sources/os/plan9/9front/sys/src/cmd/auth/enable

Small rc script to re-enable a user in mounted auth key databases.

Key responsibilities:
- Requires exactly one username argument.
- If `/mnt/keys/<user>` exists, writes `ok` to its `status`.
- If `/mnt/netkeys/<user>` exists, writes `ok` to its `status`.

Dependencies:
- Assumes `keyfs`-style key databases are mounted at `/mnt/keys` and `/mnt/netkeys`.
