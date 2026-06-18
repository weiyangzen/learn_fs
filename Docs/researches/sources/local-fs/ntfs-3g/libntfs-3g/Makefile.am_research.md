# File Research: sources/local-fs/ntfs-3g/libntfs-3g/Makefile.am

Automake rules for building the NTFS-3G core library `libntfs-3g.la`. When `INSTALL_LIBRARY` is enabled it installs the library and `libntfs-3g.pc`; otherwise the library is built as a non-installed archive. It wires compile flags through `$(AM_CFLAGS)`, `$(AM_CPPFLAGS)`, `$(LIBNTFS_CPPFLAGS)`, includes `include/ntfs-3g`, links `$(LIBNTFS_LIBS)`, and uses `-version-info $(LIBNTFS_3G_VERSION) -no-undefined`.

The source list defines the libntfs-3g implementation surface: ACL/security handling, attribute and runlist handling, bitmap/boot sector/cache/collation/compression, device and directory logic, EA/EFS/index/inode/ioctl/MFT/logfile/reparse/unicode/volume/xattr support. Conditional `NTFS_DEVICE_DEFAULT_IO_OPS` adds either `win32_io.c` or `unix_io.c`.

The install hook handles split `/usr` versus root library layouts. If `rootlibdir` differs from `libdir`, installed shared objects are moved to `rootlibdir`; `libdir` then gets either an ldscript `libntfs-3g.so` or a symlink back to the root-library copy. `uninstall-local` removes rootlib shared objects when installed.
