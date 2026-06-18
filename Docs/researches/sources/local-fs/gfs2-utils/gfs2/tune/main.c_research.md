# File Research: sources/local-fs/gfs2-utils/gfs2/tune/main.c

CLI front end for `tunegfs2`, a utility to list and modify selected GFS2 superblock fields.

Global state:
- Static `struct tunegfs2 tunegfs2_struct`
- Static pointer `tfs`

Key functions:
- `parse_mount_options`: parses `lockproto=` and `locktable=` mount-style option fragments.
- `usage`: prints syntax.
- `version`: prints `tunegfs2` version.
- `main`: parses options, opens device, reads superblock, applies requested mutations, writes back if needed, and/or lists fields.

Supported options:
- `-L <label>`: change lock table label form.
- `-U <UUID>`: change filesystem UUID.
- `-l`: list current superblock values, opens read-only.
- `-o <mount options>`: parse `lockproto=` and `locktable=`.
- `-r <version>`: change filesystem format version.
- `-V`, `-h`: version/help.

Dependencies:
- `tunegfs2.h`
- `super.c` operations
- gettext, sysexits, POSIX open/close.

Research notes:
- `-L` cannot be combined with `locktable` from `-o`.
- Writes the superblock only when a mutation option is present.
- `main` is excluded under `UNITTESTS`.
