# File Research: sources/os/linux/linux-stable/fs/fat/namei_vfat.c

This file implements the `vfat` namespace layer, including long filenames, short-alias generation, case-insensitive dentries, and extended rename behavior.

Key responsibilities:
- Provide case-sensitive or case-insensitive dentry hashing/comparison depending on mount options.
- Revalidate negative dentries when directory versions change because new long names can create matching 8.3 aliases.
- Convert user names to UTF-16 long-name slots.
- Generate unique 8.3 aliases.
- Build multi-slot VFAT directory entries.
- Implement lookup, create, mkdir, unlink, rmdir, normal rename, and `RENAME_EXCHANGE`.
- Register the `vfat` filesystem type and fs_context operations.

Important functions:
- `vfat_revalidate()` and `vfat_revalidate_ci()` validate negative dentries against parent inode version, with stricter dropping for case-insensitive create/rename targets.
- `vfat_hash()` / `vfat_hashi()` and `vfat_cmp()` / `vfat_cmpi()` implement trailing-dot-stripped dcache behavior, optionally case-insensitive through NLS lowercasing.
- `vfat_is_used_badchars()` rejects invalid Unicode names and trailing spaces.
- `to_shortname_char()` maps Unicode chars into short-name bytes, replacing unsupported or disallowed alias chars with `_` and tracking case properties.
- `vfat_create_shortname()` decides whether a long name can be represented as a short entry only, whether an LFN must be stored without a numeric tail, or whether `~n`/randomized aliases are needed to avoid collisions.
- `xlate_to_uni()` converts input names from UTF-8 or configured NLS, including `:hhhh` unicode escape decoding when enabled, and pads the UTF-16 name to 13-char slot boundaries.
- `vfat_build_slots()` builds long-name slots with checksum plus the final short alias entry.
- `vfat_add_entry()` strips trailing dots, allocates slot memory, builds slots, calls `fat_add_entries()`, and updates parent metadata.
- `vfat_lookup()` searches by long or short name, builds inodes, and handles alias dentries for long-name versus 8.3 lookups.
- `vfat_create()`, `vfat_mkdir()`, `vfat_unlink()`, and `vfat_rmdir()` are namespace mutations built around shared FAT directory helpers.
- `vfat_rename()` handles normal rename and replacement, including cross-directory `..` updates and rollback.
- `vfat_rename_exchange()` swaps two existing entries by exchanging inode `i_pos` attachments and updating `..` entries/link counts for cross-directory directory exchanges.
- `vfat_rename2()` accepts `RENAME_NOREPLACE` and `RENAME_EXCHANGE`.

Operations and registration:
- `vfat_dir_inode_operations` wires VFS namespace operations to shared FAT setattr/getattr/update_time.
- `setup()` installs vfat dir ops and selects case-insensitive dentry ops unless `check=strict`.
- The module registers `vfat_fs_type` with `fat_fill_super()` and `fat_parse_param(..., true)`.

Failure behavior:
- Invalid long names return `-EINVAL`; too-long converted names return `-ENAMETOOLONG`.
- Alias collision generation probes existing short names and falls back to jiffies-derived aliases after `~1` through `~9`.
- Rename rollback restores inode positions and dotdot entries where possible, and reports filesystem corruption if recovery fails.

Research relevance:
- This file is the Windows-compatible FAT namespace personality. It contains the highest-complexity name handling in the FAT implementation: Unicode conversion, short alias policy, negative-dentry coherency, and atomic-ish rename/exchange logic.
