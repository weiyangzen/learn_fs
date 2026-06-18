# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/uidgid.c

User/group table parsing, lookup, and console editing for `/adm/users`.

Key responsibilities:
- Defines minimal built-in users/groups in `minusers`.
- `cmd_users()` reads `/adm/users` or installs defaults with `default`.
  - First pass parses uid/name rows.
  - Sorts `uid[]` by uid.
  - Second pass parses leaders and group members into `gidspace`.
- `cmd_newuser()` and `do_newuser()` support console operations:
  - create user
  - create group
  - show entry
  - rename
  - set/remove leader
  - add/delete group member
  - rewrite `/adm/users`
  - optionally create `/usr/<name>` for low-numbered users.
- Lookup/conversion helpers:
  - `chkuid()`, `pentry()`, `setminusers()`, `uidpstr()`, `getword()`, `strtouid()`, `uidtop()`, `uidtostr()`.
- Authorization helpers:
  - `ingroup()`
  - `leadgroup()`
  - `byuid()`.
- File reading helpers:
  - `fchar()` reads buffered chunks through console fid.
  - `readln()` reads one logical line.

Important interactions:
- Uses `uidgc.uidlock` for read/write locking around uid table accesses.
- Uses console file operations (`walkto`, `con_open`, `con_read`, `con_write`) to access `/adm/users`.
- Uses global arrays `uid` and `gidspace` allocated in `main.c`.

Research notes:
- User names reject characters in `"?=+-/:"`.
- `strtouid()` returns `-2` for unknown user; other callers often interpret `-1` specially for adm.
- `cmd_users()` requires `conf.nuid` and `conf.gidspace` to be large enough; it prints diagnostics but continues where possible.
