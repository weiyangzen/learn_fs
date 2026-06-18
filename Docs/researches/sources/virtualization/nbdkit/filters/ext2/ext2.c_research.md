# File Research: sources/virtualization/nbdkit/filters/ext2/ext2.c

Implements the `nbdkit ext2` filter, exposing a regular file inside an ext2-family filesystem image as an NBD export. The required `ext2file=` parameter is either an absolute in-image path or `exportname`, in which case each client export name selects the embedded file.

The filter opens a single shared ext2 filesystem in `.after_fork` using `ext2fs_open()` and the custom `nbdkit_io_manager` from `io.c`. Per-connection handles store the client export name, resolved inode, `ext2_file_t`, and filter context.

`ext2_prepare()` resolves the path with `ext2fs_namei()`, rejects non-regular files, opens the inode with `ext2fs_file_open2()`, and binds the shared backend context into the connection with `nbdkit_context_set_next()`. Reads and writes loop through `ext2fs_file_llseek()`, `ext2fs_file_read()`, and `ext2fs_file_write()`.

The filter serializes all requests because libext2fs is not generally re-entrant. It disables multi-conn, supports native FUA by flushing the ext2 file, emulates cache through reads, and does not expose trim/zero optimizations. Flush maps to `ext2fs_file_flush()`.
