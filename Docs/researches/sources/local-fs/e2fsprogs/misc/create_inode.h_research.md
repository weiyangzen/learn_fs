# File Research: sources/local-fs/e2fsprogs/misc/create_inode.h

## Purpose
Declares the filesystem population and inode creation API used by mke2fs-related code.

## Types / Flags
- `struct hdlink_s` and `struct hdlinks_s` track source hardlinks mapped to destination inode numbers.
- `struct file_info` stores a growable target path buffer.
- `POPULATE_FS_NO_COPY_XATTRS` disables xattr copying.
- `POPULATE_FS_LINK_APPEND` changes directory link insertion behavior.
- `struct fs_ops_callbacks` provides optional create/end-create hooks.

## API Surface
Declares:
- `populate_fs()`, `populate_fs2()`, `populate_fs3()`.
- Internal-style creators for mknod, symlink, mkdir, and file copy.
- `add_link()` for hardlink creation.
- `set_inode_extra()` for uid/gid/mode/time metadata.

## Integration
Implemented primarily by `create_inode.c`, with tar population delegated through libarchive support.

## Risks / Notes
The header exposes helpers named “internal” to other misc code, so callers need to honor expected cwd/root/path semantics.
