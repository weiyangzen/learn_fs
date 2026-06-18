# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/fsck.ocfs2.8.in

Read coverage: complete file read, 142 lines.

Purpose: manual page template for `fsck.ocfs2`.

Content:
- Documents synopsis, device argument, options, exit codes, related tools, authors, and copyright.
- Highlights repair modes: `-n` no-write diagnostics, `-y` answer yes, `-p` preen, and `-a` compatibility alias for `-p`.
- Documents cluster-safety option `-F` with explicit corruption warning.
- Documents backup superblock recovery with `-r`, alternate superblock/block size with `-b`/`-B`, forced check with `-f`, directory optimization with `-D`, progress/stats/debug/version options.

Exit-code contract:
- Matches e2fsck-style bitmask: `0`, `1`, `2`, `4`, `8`, `16`, `32`, and `128`.

Risk notes:
- The man page is the user-visible safety contract for dangerous options.
- It points detailed repair prompts to `fsck.ocfs2.checks(8)`.
