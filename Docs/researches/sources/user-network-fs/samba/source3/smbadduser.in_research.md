# sources/user-network-fs/samba/source3/smbadduser.in

Purpose: legacy C shell utility template for adding UNIX users to Samba password and username-map files.

Important functions and APIs: uses substituted install variables (`@prefix@`, `@libdir@`, `@privatedir@`, `@configdir@`), `getent passwd` by default, `awk`, `grep`, and `smbpasswd`. It expects arguments in `unixid:ntid` form.

Control flow: with no arguments it prints usage. It ensures `$PRIVATEDIR/smbpasswd` and `$CONFIGDIR/smbusers` exist, then iterates each mapping. For each entry it validates the colon format, extracts UNIX and NT IDs, checks the UNIX account exists, checks it is not already in smbpasswd, runs `smbpasswd -a -n unix`, appends a username-map line if UNIX and NT IDs differ, records the new UNIX name, and finally prompts interactively for each new user's password via `smbpasswd`.

State and persistence: mutates the private `smbpasswd` file and config `smbusers` map, and invokes `smbpasswd` to set password state.

Dependencies and integration: depends on C shell, local passwd database, old smbpasswd backend paths, and interactive terminal input. It is a compatibility/admin script, not part of automated selftest.

Risks and test signals: the script hard-codes `/usr/bin/smbpasswd` for initial add while later using PATH `smbpasswd`; it appends maps without locking and is not safe for concurrent edits. It should be considered legacy and high-risk in modern deployments.
