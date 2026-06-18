# File Research: sources/local-fs/e2fsprogs/misc/mke2fs.conf.in

`mke2fs.conf.in` is the default `mke2fs` configuration template.

Defaults:
- `base_features = sparse_super,large_file,filetype,resize_inode,dir_index,ext_attr`
- `default_mntopts = acl,user_xattr`
- `enable_periodic_fsck = 0`
- `blocksize = 4096`
- `inode_size = 256`
- `inode_ratio = 16384`

Filesystem type stanzas:
- `ext3` adds `has_journal`.
- `ext4` enables modern ext4 defaults:
  - `has_journal`
  - `extent`
  - `huge_file`
  - `flex_bg`
  - `metadata_csum`
  - `metadata_csum_seed`
  - `64bit`
  - `dir_nlink`
  - `extra_isize`
  - `orphan_file`
- `small` and `floppy` force 1024-byte block size and denser inode ratios.
- `big`, `huge`, `news`, `largefile`, and `largefile4` tune inode density.
- `largefile` and `largefile4` use `blocksize = -1`, allowing `mke2fs.c` to choose a heuristic/page-size block size subject to a minimum.
- `hurd` forces 4096-byte blocks, 128-byte inodes, and disables Y2038 warning.

Research notes:
- This template is used both for installation and, through `profile-to-c.awk`, as the source of an embedded default profile.
- The ext4 stanza reflects current defaults expected by `mke2fs.c`, including metadata checksumming and orphan file support.
