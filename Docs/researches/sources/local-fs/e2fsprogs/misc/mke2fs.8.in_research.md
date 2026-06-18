# File Research: sources/local-fs/e2fsprogs/misc/mke2fs.8.in

`mke2fs.8.in` is the generated-source manual page template for `mke2fs`, `mkfs.ext2`, `mkfs.ext3`, and `mkfs.ext4`.

Documented purpose:
- Create ext2, ext3, or ext4 filesystems on a block device or image file.
- Infer fs type from invocation name such as `mkfs.ext4` unless overridden with `-t`.
- Use `/etc/mke2fs.conf` defaults unless command-line options override them.

Major option coverage:
- Geometry and sizing: `-b`, `-C`, `-g`, `-G`, `fs-size`.
- Inode layout: `-i`, `-I`, `-N`.
- Journaling: `-j`, `-J size=`, `-J device=`, `-J location=`, `-J fast_commit_size=`.
- Features: `-O`, including enable/disable syntax and reference to `ext4(5)`.
- Extended options: `-E`, including discard, lazy initialization, casefold encoding, hash seed, packed metadata, offset, resize reservation, quotas, root ownership/perms/SELinux label, orphan file size, RAID stride/stripe, test_fs.
- Safety/operation: `-c`, `-l`, `-D`, `-F`, `-n`, `-S`, `-q`, `-v`, `-V`, `-z`.
- Metadata strings: `-L`, `-M`, `-U`, `-o`.
- Usage profiles: `-T`.

Environment variables:
- `MKE2FS_SYNC`
- `MKE2FS_CONFIG`
- `MKE2FS_FIRST_META_BG`
- `MKE2FS_DEVICE_SECTSIZE`
- `MKE2FS_DEVICE_PHYS_SECTSIZE`
- `MKE2FS_SKIP_CHECK_MSG`

Research notes:
- The page closely matches behavior implemented in `mke2fs.c`, especially extended options parsed by `parse_extended_opts()`.
- It explicitly warns that `-S` is a last-resort recovery mode requiring exact recreation of original layout parameters.
- It documents undo-file limitations: undo cannot recover from power or system crash.
