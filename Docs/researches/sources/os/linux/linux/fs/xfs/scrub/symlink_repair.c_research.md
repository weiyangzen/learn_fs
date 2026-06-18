# File Research: sources/os/linux/linux/fs/xfs/scrub/symlink_repair.c

This file implements online repair for corrupted XFS symbolic links. It attempts to salvage a plausible target, writes a repaired target into a hidden temporary symlink, atomically exchanges data fork contents with the damaged symlink, and reaps/reset old blocks.

Key entry points:
- `xrep_setup_symlink(struct xfs_scrub *sc, unsigned int *resblks)`: creates an `S_IFLNK` tempfile and reserves enough blocks for max symlink target plus bmbt overhead.
- `xrep_symlink(struct xfs_scrub *sc)`: main repair function.

Salvage logic:
- `xrep_symlink_salvage_inline`: copies local fork bytes unless inode repair already zapped the target to `?`.
- `xrep_symlink_salvage_remote`: reads mapped remote symlink blocks manually, accepts blocks when offset/byte/owner header checks pass and either verifier passes or magic is intact, then copies payload bytes.
- `xrep_symlink_salvage`: uses salvage only if initial scrub did not already flag direct corruption; NUL-terminates the buffer; requires `strlen(buffer) == i_disk_size`; otherwise substitutes a long dummy target.

Dummy target:
- The replacement message is deliberately longer than `NAME_MAX` but within XFS symlink max length, so resolving it should fail with name-too-long instead of accidentally pointing to a real path.

Rebuild/exchange flow:
1. Require `rmapbt` for old fork reaping and exchange-range for atomic commit.
2. Salvage target into `sc->buf`.
3. Unlock the damaged inode, lock the tempfile, reserve quota/blocks, destroy dummy target fork, and write the target with `xfs_symlink_write_target`.
4. Commit the repair transaction before computing exchange reservation.
5. Allocate exchange transaction and lock both inodes.
6. If both old and new targets are local and the new target fits the repaired inode fork, copy local fork bytes directly.
7. Otherwise convert local forks to extent format as needed and call `xrep_tempexch_contents`.
8. Reap old remote blocks from the temporary file and reset its fork to a short dummy symlink.

Important helpers:
- `xrep_symlink_local_to_remote`: wraps local-to-remote conversion and fixes CRC symlink owner.
- `xrep_symlink_swap_prep`: promotes local forks to exchangeable extent format.
- `xrep_symlink_swap`: chooses direct local copy vs mapping exchange.
- `xrep_symlink_reset_fork`: frees old blocks and rewrites tempfile target to `?`.

Risk notes:
- Readlink can still see old corrupted contents while repair writes the hidden tempfile because VFS does not take IOLOCK for symlink reads.
- Salvage is conservative: mismatched length or embedded NUL causes fallback to dummy target.
- The file depends on atomic mapping exchange to avoid exposing partially rebuilt symlink contents.
