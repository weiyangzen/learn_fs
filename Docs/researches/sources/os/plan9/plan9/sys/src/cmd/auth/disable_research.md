# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/disable

Shell script to disable a user in both auth key databases.

Key points:
- If `/mnt/keys/$1` exists, writes `disabled` to its `status`.
- If `/mnt/netkeys/$1` exists, writes `disabled` to its `status`.

Dependencies:
- Plan 9 `rc` shell and mounted key databases.

Notable behavior:
- Does not validate arguments or report missing users.
