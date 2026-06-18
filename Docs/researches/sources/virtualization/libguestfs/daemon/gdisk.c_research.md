# File Research: sources/virtualization/libguestfs/daemon/gdisk.c

Small GPT helper using `sgdisk`.

Important behavior:
- `optgroup_gdisk_available` checks for `sgdisk`.
- `do_part_expand_gpt(device)` runs `sgdisk -e <device>`.
- Folds stdout onto stderr for better error reporting.

Filesystem relevance: repairs/expands GPT metadata to the full disk size after virtual disk growth.
