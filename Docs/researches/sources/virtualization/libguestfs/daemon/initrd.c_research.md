# File Research: sources/virtualization/libguestfs/daemon/initrd.c

Lists and extracts files from compressed initrd/cpio archives.

Important behavior:
- `do_initrd_list` runs a quoted `zcat <sysroot path> | cpio --quiet -it` pipeline and returns line-split filenames.
- `do_initrd_cat` extracts one named file into a temporary directory with `cpio --quiet -id`.
- Enforces `GUESTFS_MESSAGE_MAX` before returning extracted file contents.
- Cleans up extracted file and containing temporary directories.
- Uses shell quoting for archive path, temp directory, and requested filename.

Filesystem relevance: inspects boot initramfs contents stored in guest filesystems.
