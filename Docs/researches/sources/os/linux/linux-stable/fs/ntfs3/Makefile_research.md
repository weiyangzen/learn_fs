# File Research: sources/os/linux/linux-stable/fs/ntfs3/Makefile

This Makefile builds the `ntfs3` filesystem module or built-in object and configures warning coverage for the driver.

Main responsibilities:
- Adds a subset of W=1 style warnings and suppresses selected `-Wextra` warnings that are noisy for this codebase.
- Builds `ntfs3.o` when `CONFIG_NTFS3_FS` is enabled.
- Lists core object files for attributes, attribute lists, bitmaps, directories, records, files, journal/log handling, inodes, index logic, compression, namei, runlists, superblock, upcase, and xattrs.
- Adds external compression library objects when `CONFIG_NTFS3_LZX_XPRESS` is enabled.

Research notes:
- The prompt listed 56 lines, while the checked-out file contains 55 lines.
- The object list shows that the files in this group are foundational components of the broader ntfs3 driver, not standalone code.
