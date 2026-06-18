# File Research: sources/virtualization/libguestfs/daemon/ext2.c

Large ext2/ext3/ext4 daemon adapter for e2fsprogs-backed operations.

Key points:
- Recognizes `ext2`, `ext3`, and `ext4` via `fstype_is_extfs`.
- Parses `tune2fs -l` output into alternating key/value strings, normalizing `<none>`, `<not available>`, and `(none)` to empty.
- Implements e2 label/UUID get/set, resize variants, minimum-size query, fsck, external journal creation/use, general `tune2fs`, ext attributes, generation get/set, full `mke2fs`, and `mklost+found`.
- Runs `e2fsck -f` before resize when the target filesystem is not mounted.
- `ext_minimum_size` parses `resize2fs -P -f` block count, retrieves block size from `tune2fs`, checks overflow, and returns bytes.
- `do_e2fsck` enforces mutual exclusion among `correct`, `forceall`, and `forceno`; accepts e2fsck exit 0 or 1 only.
- Label length is limited to `EXT2_LABEL_MAX` bytes.
- `do_mke2fs` maps a large optional-argument surface into `mke2fs` flags and validates non-negative numeric options.
- Journal device optional argument manually performs device-name translation when needed.
- File attributes are validated for allowed ASCII letters, duplicates, and chattr-reserved letters before invoking `chattr`.
