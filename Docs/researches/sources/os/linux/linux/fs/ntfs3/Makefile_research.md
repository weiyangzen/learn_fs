# File Research: sources/os/linux/linux/fs/ntfs3/Makefile

Read coverage: complete file, 56 lines.

This Makefile builds the `ntfs3` kernel module or built-in object set.

Key contents:
- Adds a subset of `W=1` warnings plus compiler-option-guarded warning flags.
- Suppresses selected `-Wextra` warnings that are noisy for this codebase.
- Builds `ntfs3.o` when `CONFIG_NTFS3_FS` is enabled.
- Core object list includes attribute, bitmap, directory, log, inode, index, runlist, superblock, upcase, xattr, compression, and namei/file support objects.
- Adds `lib/decompress_common.o`, `lib/lzx_decompress.o`, and `lib/xpress_decompress.o` when `CONFIG_NTFS3_LZX_XPRESS` is enabled.

Integration:
- Mirrors Kconfig feature selection.
- Sets stricter local warning policy than many kernel subdirectories.

Risk:
- Warning flags may expose compiler-version-specific issues; guarded flags reduce but do not eliminate portability concerns.
