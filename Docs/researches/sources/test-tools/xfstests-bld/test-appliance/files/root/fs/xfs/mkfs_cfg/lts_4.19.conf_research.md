# sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_4.19.conf

- Purpose: xfs mkfs profile lts_4.19.conf; it defines named mkfs defaults consumed by the xfs config when runtests.sh is invoked with mkfs_config=lts_4.19. The file is 20 lines/255 bytes and is researched as source path `sources/test-tools/xfstests-bld/test-appliance/files/root/fs/xfs/mkfs_cfg/lts_4.19.conf`.
- Important APIs/types/functions: INI-style mkfs profile sections `metadata, inode, naming` with options bigtime=0, crc=1, finobt=1, inobtcount=0, reflink=0, rmapbt=0, autofsck=0, sparse=1, nrext64=0, exchange=0.
- Control flow: the filesystem config reads this profile when `MKFS_CONFIG` names it, combines the section options with command-line mkfs overrides, and passes the result to mkfs during `runtests.sh`.
- State and persistence: no runtime state by itself; it changes the on-disk format features of newly formatted scratch/test filesystems.
- Dependencies/integration: consumed by ext4 or xfs config hooks and indirectly by `parse_cli --mkfs-config`/`runtests.sh`.
- Risks and test signals: obsolete feature combinations may be rejected by newer tools or mismatch an intended LTS baseline; validate by formatting a disposable test device and checking recorded mkfs options in result config.
