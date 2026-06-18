# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-1234.c

This helper file provides shared directory validation and cleanup for all unsquashfs format readers.

Key functions:
- `check_name`: validates one directory entry name.
- `squashfs_closedir`: frees a `struct dir` and its linked entries.
- `check_directory`: verifies directory entries are strictly sorted and have no duplicates.

Name validation rules:
- Rejects `.`, `./`, `..`, and `../`.
- Rejects any slash in the entry name.
- Rejects names shorter than the expected size.

Directory validation:
- Requires strictly increasing `strcmp` order for adjacent names.
- Because duplicates would sort adjacent, `strcmp >= 0` rejects both duplicates and unsorted entries.

Importance:
- This file is part of corruption hardening. It prevents malicious directory entries from escaping extraction paths or hiding duplicates through ordering tricks.
