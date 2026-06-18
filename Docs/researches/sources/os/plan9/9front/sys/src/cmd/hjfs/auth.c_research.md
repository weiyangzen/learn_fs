# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/auth.c

Manages `hjfs` users, groups, permissions, and user database updates.

Key points:
- Defines built-in default users/groups including `adm`, `none`, `tor`, `glenda`, `sys`, `map`, `doc`, `upas`, and `font`.
- Validates user names by rejecting empty names, control characters, and selected punctuation.
- Parses user database lines in `uid:name:leader:member,member` format.
- `usersload()` reads a user database file through a `Chan`, parses it, resolves names to uids, sorts users and memberships, and atomically swaps `fs->udata`.
- `userssave()` writes the current or default user database through a `Biobuf`, optionally using channel-backed append writes.
- `lookupuid()`, `uid2name()`, and `name2uid()` provide uid/name resolution.
- `ingroup()` checks direct identity, group leader, and membership.
- `permcheck()` evaluates Plan 9-style owner/group/other read/write/execute permissions, unless `FSNOPERM` is set.
- `cmdnewuser()` implements the console `newuser` command:
  - creates users/groups
  - renames users
  - changes leader
  - adds/removes memberships
  - writes updated users
  - optionally creates `/usr/<name>`

Dependencies and interactions:
- Uses core `Chan` operations to read/write users and create user directories.
- Called by 9P attach and permission checks.
- Exposes administrative command hooks used by `cons.c`.

Research relevance:
- Defines `hjfs` identity and permission semantics, including mutable user database behavior.
