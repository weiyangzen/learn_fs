# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/util.c

`util.c` provides shared helper routines for `tapefs` backends.

Functions:
- `getpass` parses passwd/group-style files into a dynamically grown `Idmap` array using colon-delimited fields, storing field 0 as name and field 2 as numeric id.
- `mapid` maps numeric ids through an `Idmap`, falling back to decimal string.
- `poppath` inserts a `Fileinf` path into the `Ram` tree, recursively creating parent directories when path components contain `/`, handling trailing slash as directory, resolving `.` to root, and updating existing entries when `new` is true.
- `popfile` allocates and links a `Ram` node under a directory.
- `lookup` finds an existing active child by name.

Behavioral notes:
- `poppath` forces at least user-read bit on modes.
- If an existing node changes file-vs-directory type, it warns and ignores the replacement.
- Owner/group names are derived with `mapid`.

Risks:
- `getpass` uses `strdup` directly for names while other allocation uses tapefs helpers.
- Path insertion mutates `fi.name` while preserving a duplicate for diagnostics.
