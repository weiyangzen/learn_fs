# File Research: sources/virtualization/libguestfs/daemon/blkid.c

Provides blkid-backed filesystem metadata queries.

Key points:
- `get_blkid_tag` runs `blkid -c /dev/null -o value -s TAG device`, treats exit status `2` as “tag not found,” and trims trailing newline.
- `do_vfs_label` delegates to Btrfs or NTFS label helpers when appropriate, otherwise uses blkid `LABEL`.
- `do_vfs_uuid` uses blkid `UUID`.
- `do_blkid` probes once whether blkid supports `-p` and `-i`.
- Modern path parses `blkid -p -i -o export` into alternating key/value strings; fallback returns only `TYPE`, `LABEL`, and `UUID`.
