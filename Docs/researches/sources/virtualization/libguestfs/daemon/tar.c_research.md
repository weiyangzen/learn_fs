# File Research: sources/virtualization/libguestfs/daemon/tar.c

## Role
Implements tar-based archive upload and download actions, including compressed variants and optional preservation of xattrs, SELinux labels, ACLs, numeric owners, and directory symlinks.

## Tar In
- `do_tar_in()` receives a FileIn stream and pipes it into `tar -C <sysroot-dir> -xf -`.
- Supports compression filters: compress, gzip, bzip2, xz, lzop, lzma, and zstd.
- Checks whether `chown` is supported on the target filesystem and adds `--no-same-owner` when needed.
- Captures tar stderr in a temporary error file so upload failures can report meaningful errors.
- `do_tgz_in()` and `do_txz_in()` are gzip/xz compatibility wrappers.

## Tar Out
- `do_tar_out()` verifies the target is a directory, builds a tar command, replies before streaming, then sends FileOut chunks.
- Supports excludes through a temporary `-X` exclude file.
- On read or subprocess failure after the protocol reply, it cancels the file transfer with `send_file_end(1)`.
- `do_tgz_out()` and `do_txz_out()` are gzip/xz wrappers.

## Filesystem/Storage Relevance
This is the daemon’s bulk tree import/export path for guest filesystems, preserving filesystem metadata when requested.
