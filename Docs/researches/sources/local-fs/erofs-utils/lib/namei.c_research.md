# File Research: sources/local-fs/erofs-utils/lib/namei.c

This file implements on-disk inode reading and path lookup inside an EROFS image.

Inode reading:
- `erofs_read_inode_from_disk(struct erofs_inode *vi)` reads compact or extended inode structures from metadata or metabox storage.
- It validates `i_format`, datalayout, inode version, chunk format, and file mode.
- It handles extended inode records crossing block boundaries.
- It fills inode size, uid/gid, nlink, mtime, xattr ibody size, flat block address, device number, chunk format, and dot-omitted flag.
- Compact inode handling supports the special nlink-1/startblk_hi encoding and respects 32-bit vs 48-bit address masks.

Directory lookup:
- `find_target_dirent()` scans a directory block’s dirent table and compares names while validating name offsets and lengths.
- `erofs_namei()` opens a directory inode with `erofs_iopen()`, reads directory blocks through `erofs_pread()`, validates the first `nameoff`, and returns the target child NID.
- `link_path_walk()` walks slash-separated components from root.
- `erofs_ilookup()` resolves a path into an inode by NID and then reads the inode from disk.

Important behavior:
- Short or malformed directory entries return `-EFSCORRUPTED`.
- Directory block scanning uses `nameoff` as the boundary between dirent records and name strings.
- Device numbers use local Linux-compatible decode logic.

Dependencies:
- Metadata buffer reading via `erofs_read_metabuf`.
- File data reads via `erofs_iopen` / `erofs_pread`.
- Endian conversion and on-disk EROFS structs.

Risk / note:
- This is read-side validation code used by rebuild, incremental, and lookup flows; corruption handling here directly affects importer robustness.
