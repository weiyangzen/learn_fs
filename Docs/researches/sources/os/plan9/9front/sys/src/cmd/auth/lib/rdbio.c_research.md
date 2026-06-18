# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/rdbio.c

Reader and clearer for account biography records.

Key responsibilities:
- Frees and clears all dynamically allocated fields in `Acctbio`.
- Reads pipe-separated bio records from a file.
- Selects records matching the requested user.
- Populates post id, name, department, and up to `Nemail` email fields.
- Always sets `a->user` to the requested user.

Dependencies:
- Uses Plan 9 `Biobuf` and `getfields`.
