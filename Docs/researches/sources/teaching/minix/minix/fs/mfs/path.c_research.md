# File Research: sources/teaching/minix/minix/fs/mfs/path.c

`path.c` contains MFS path-component lookup and directory-entry manipulation. `fs_lookup` receives an already-open directory inode number, looks up a component with `advance`, and returns inode metadata plus mountpoint status while leaving the target inode open for VFS.

`advance` validates nonempty names, rejects deleted directories, searches the directory with `search_dir(..., LOOK_UP)`, and opens the target inode by number.

`search_dir` is the central directory engine. It implements lookup, insertion, deletion, and emptiness checks over fixed-size `struct direct` entries. It validates directory type, rejects mutations on read-only filesystems, scans directory blocks with `get_block_map`, compares names using only `MFS_NAME_MAX` bytes, and treats only `.` and `..` as allowed entries for `IS_EMPTY`.

For deletion, it stores the deleted inode number in the tail of the name field as recovery metadata, clears `mfs_d_ino`, dirties the directory block, updates parent times, and adjusts `i_last_dpos`. For insertion, it reuses a free slot or extends the directory with `new_block`, zero-fills the name field, truncates/copies the new name, writes the inode number with byte-order conversion, updates size when needed, and writes the inode immediately if the directory grew.
