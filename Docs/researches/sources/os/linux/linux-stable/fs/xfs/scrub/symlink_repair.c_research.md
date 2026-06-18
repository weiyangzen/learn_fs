# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/symlink_repair.c

Implements online repair for symlink targets.

Repair strategy:
- Salvage existing target bytes when possible.
- If salvage produces exactly `i_disk_size` bytes before NUL termination, rewrite that target.
- Otherwise replace the target with an intentionally overlong explanatory dummy target that should not resolve to a real path.
- Write the replacement into a hidden temporary symlink and commit it by file contents exchange.

Key behavior:
- `xrep_setup_symlink` creates a hidden symlink tempfile and reserves maximum symlink block and bmbt exchange overhead.
- `xrep_symlink_salvage_remote` reads remote target extents manually, accepts salvage only when headers are plausible and either verifiers pass or magic is correct, and stops at the first unsafe block.
- `xrep_symlink_salvage_inline` copies inline fork bytes unless inode repair had already zapped the target to `?`.
- `xrep_symlink_salvage` accepts salvaged data only if string length equals `i_disk_size`; otherwise installs `DUMMY_TARGET`.
- `xrep_symlink_rebuild` writes the salvaged/dummy target into the tempfile, commits, allocates exchange state, swaps contents, then resets the tempfile fork.
- `xrep_symlink_swap` optimizes local-to-local replacement by copying fork data directly if it fits; otherwise it promotes local forks to extent form and uses mapping exchange.
- `xrep_symlink_reset_fork` reaps old remote blocks and rewrites the tempfile to a minimal valid dummy target.

Important constraints:
- Requires `rmapbt` to reap the old fork and exchange-range support to commit atomically.
- Uses transaction commits and relocking to satisfy exchange reservation and locking rules.
- Does not promise that concurrent `readlink` cannot see old corrupt contents during rebuild.
