# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/con.c

This file implements the KFS command language served through the `.cmd` service file.

Key behavior:
- `consserve` initializes the console session, attaches the default filesystem, and loads users.
- `cmd_exec` dispatches text commands through the `command[]` table.
- Implements operator commands: `allow`, `allowoff`, `atime`, `cfs`, `chat`, `check`, `clri`, `create`, `halt`, `help`, `listen`, `newuser`, `noneattach`, `nowritegroup`, `remove`, `rename`, `start`, `stats`, `sync`, `user`.
- `cmd_check` translates single-letter options into checker flags and invokes `check`.
- `cmd_create`, `cmd_remove`, `cmd_rename`, and `cmd_clri` use console 9P calls to modify the filesystem.
- `cmd_newuser` appends to `/adm/users` and creates a default home tree.
- `cmd_listen` starts network service, defaulting to `tcp!*!564`.

Parsing helpers:
- `skipbl`, `cname`, `_cname`, `nextelem`, and `number` parse command arguments, names, paths, and numbers.

Dependencies:
- Uses console 9P wrappers from `console.c`.
- Uses old stat conversion from `9p1lib.c`.
- Uses uid/group state from `uid.c`.
- Uses checker from `chk.c`.

Notable detail:
- Some console operations bypass normal user identity by using `cons.uid` and `cons.gid`, explicitly described in comments as a botch.
