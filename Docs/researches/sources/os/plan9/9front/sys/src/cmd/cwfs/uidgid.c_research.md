# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/uidgid.c

Purpose: User/group database loading, lookup, editing, and permission helper support for cwfs.

Key behavior:
- `cmd_users()` loads `/adm/users` or a supplied file through the cwfs console path. It parses uid/name/leader/member records in two passes: first users, then group memberships.
- `setminusers()` installs a minimal built-in user table when `users default` is requested.
- `cmd_newuser()` and `do_newuser()` implement console user/group edits: create user/group, query, rename, set/remove leader, add/remove group member, then rewrite `/adm/users`.
- `uidpstr()`, `uidtop()`, `strtouid()`, and `uidtostr()` perform name/id lookup using the sorted uid table.
- `ingroup()` and `leadgroup()` support permission checks from `sub.c`.
- `pentry()` serializes a `Uid` back to `/adm/users` format.
- `readln()` and `fchar()` read `/adm/users` via console file operations and a temporary `Iobuf`.

Notable details:
- Group space is a single `gidspace` array; edits that add members copy the group table to the current tail.
- Built-in users include `adm`, `none`, `tor`, `sys`, `map`, `doc`, `upas`, `font`, and `bootes`.
- Names reject characters from `"?=+-/:"` and enforce `NAMELEN`.
