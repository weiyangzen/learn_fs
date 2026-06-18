# File Research: sources/local-fs/e2fsprogs/misc/mke2fs-hurd.conf

`mke2fs-hurd.conf` is a compact default configuration for creating ext filesystems for GNU Hurd compatibility.

Contents:
- `[defaults]` enables conservative ext features:
  - `sparse_super`
  - `filetype`
  - `resize_inode`
  - `dir_index`
  - `ext_attr`
- Default mount options are `acl,user_xattr`.
- Periodic fsck is disabled.
- Default block size is 4096.
- Default inode size is 128, matching Hurd limitations.
- Default inode ratio is 16384.

Filesystem type stanzas:
- `ext3` adds `has_journal`.
- `ext4` adds journal, extents, huge file support, flex_bg, uninitialized groups, dir_nlink, and extra inode size, with `auto_64-bit_support = 1` and inode size 256.
- Usage profiles tune inode density:
  - `small`, `floppy`, `news`: denser inode ratios.
  - `big`, `huge`, `largefile`, `largefile4`: sparser inode ratios.
- `hurd` forces block size 4096 and inode size 128.

Research notes:
- Compared with the general `mke2fs.conf.in`, this configuration omits newer default ext4 features such as metadata checksums, checksum seed, 64bit, and orphan_file.
- The `hurd` stanza is designed to be appended by `mke2fs.c` when the creator OS is Hurd.
