# File Research: sources/local-fs/e2fsprogs/misc/tune2fs.8.in

`tune2fs.8.in` is the manual page template for `tune2fs`, the ext2/ext3/ext4 filesystem tuning utility.

Documented purpose:
- Adjust tunable filesystem parameters on an existing ext filesystem.
- Display current superblock settings with `-l`.
- Accept device paths and `LABEL=`/`UUID=` specifiers.

Major option coverage:
- Check scheduling: `-c`, `-C`, `-i`, `-T`.
- Error behavior: `-e`.
- Force behavior: `-f`, including warnings for external journal removal and unreplayed journals.
- Ownership/reservation: `-g`, `-u`, `-m`, `-r`.
- Inode size conversion: `-I`, with warnings about required fsck and interruption risk.
- Journaling: `-j`, `-J device=`, `-J size=`, `-J location=`, `-J fast_commit_size=`.
- Labels and mount metadata: `-L`, `-M`, `-o`, `-E mount_opts=`.
- Feature toggling: `-O`.
- Quotas: `-Q usrquota`, `grpquota`, `prjquota` and negated forms.
- UUID changes: `-U clear|random|time|uuid`.
- Undo support: `-z`.

Extended options documented:
- `clear_mmp`
- `encoding`
- `encoding_flags`
- `force_fsck`
- `hash_alg`
- `mmp_update_interval`
- `mount_opts`
- `orphan_file_size`
- `stride`
- `stripe_width`
- `test_fs`
- `^test_fs`

Feature documentation:
- Lists tunable features such as `64bit`, `casefold`, `dir_index`, `dir_nlink`, `ea_inode`, `encrypt`, `extent`, `extra_isize`, `filetype`, `flex_bg`, `has_journal`, `fast_commit`, `large_dir`, `huge_file`, `large_file`, `metadata_csum`, `metadata_csum_seed`, `mmp`, `orphan_file`, `project`, `quota`, `read-only`, `resize_inode`, `sparse_super`, `stable_inodes`, `uninit_bg`, and `verity`.
- Notes that some features are only settable or only clearable by `tune2fs`.
- Advises follow-up `e2fsck` for some feature changes.

Research notes:
- This file is documentation only, but it overlaps conceptually with `mke2fs.c` options for journals, features, quotas, encoding, MMP, orphan files, and undo.
- It documents post-creation mutation paths for many fields initially established by `mke2fs`.
