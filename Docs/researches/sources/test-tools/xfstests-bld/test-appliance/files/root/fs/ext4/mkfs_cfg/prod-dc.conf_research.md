# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext4/mkfs_cfg/prod-dc.conf

- Purpose: ext4 mkfs profile prod-dc.conf; it defines named mkfs defaults consumed by the ext4 config when runtests.sh is invoked with mkfs_config=prod-dc. The file is 13 lines/305 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/ext4/mkfs_cfg/prod-dc.conf`.
- Important APIs/types/functions: INI-style mkfs profile sections `defaults, fs_types` with options blocksize = 4096, inode_size = 128, inode_ratio = 20480, reserved_ratio = 1.0, lazy_itable_init = false, ext4 = {, features = ^ext_attr,^resize_inode,^has_journal,extents,huge_file,flex_bg,uninit_bg,dir_nlink,sparse_super, hash_alg = half_md4.
- Control flow: the filesystem config reads this profile when `MKFS_CONFIG` names it, combines the section options with command-line mkfs overrides, and passes the result to mkfs during `runtests.sh`.
- State and persistence: no runtime state by itself; it changes the on-disk format features of newly formatted scratch/test filesystems.
- Dependencies/integration: consumed by ext4 or xfs config hooks and indirectly by `parse_cli --mkfs-config`/`runtests.sh`.
- Risks and test signals: obsolete feature combinations may be rejected by newer tools or mismatch an intended LTS baseline; validate by formatting a disposable test device and checking recorded mkfs options in result config.
