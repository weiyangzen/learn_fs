# File Research: sources/local-fs/e2fsprogs/misc/e2label.8.in

## Purpose
Manual page template for `e2label`, which displays or changes ext2/ext3/ext4 volume labels.

## Documented Interface
- `e2label device`
- `e2label device volume-label`

## Behavior Described
- Without `volume-label`, prints the current label.
- With `volume-label`, sets the filesystem label.
- Ext labels are at most 16 characters; longer labels are truncated with a warning.
- Mentions that mounted filesystems with online label support may also work and may not use the same truncation path.

## See Also
- `mke2fs`
- `tune2fs`
