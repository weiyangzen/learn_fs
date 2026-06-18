# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/uid.c

This file manages KFS user, group, and membership tables, loaded primarily from `/adm/users`.

Key behavior:
- `cmd_user` reads `/adm/users` through console 9P calls and builds `uid`, `uidspace`, and `gidspace`.
- If `/adm/users` cannot be read, initializes a minimal built-in table with users/groups such as `adm`, `none`, `glenda`, `sys`, `upas`, and `bootes`.
- `fname` and `fchar` stream and tokenize `/adm/users`.
- `uidtostr`/`uidtostr1` map numeric ids to names.
- `strtouid`/`strtouid1` map names to numeric ids.
- `ingroup` tests group membership using flattened `gidspace`.
- `leadgroup` checks group leader authority.

Data handling:
- Uses `uidgc.uidlock` to protect user/group state.
- Sorts by uid and by name to report duplicates.
- Sets global `writegroup` to the uid of group/user name `"write"`.

Notable detail:
- `strtouid1` returns `0` both for unknown names and for `none`, so callers often treat `0` as “unknown/none” carefully.
