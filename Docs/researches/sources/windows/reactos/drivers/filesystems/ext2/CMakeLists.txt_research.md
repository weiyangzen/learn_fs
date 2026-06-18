# File Research: sources/windows/reactos/drivers/filesystems/ext2/CMakeLists.txt

Build definition for the ReactOS `ext2fs` kernel-mode filesystem driver.

Key behavior:
- Adds include directories for ReactOS driver headers and the local `inc` directory.
- Builds `ext2fs` as a module from ext2/ext3/ext4, JBD, NLS, core dispatch, cache, I/O, PnP, shutdown, read, write, and `inc/ext2fs.h` sources.
- Defines `_CRT_NON_CONFORMING_SWPRINTFS` on the target.
- Suppresses compiler-specific warnings for MSVC, GCC, and Clang.
- Links `memcmp` and `${PSEH_LIB}`.
- Adds global definitions `__KERNEL__`, `_CRT_NO_POSIX_ERROR_CODES`, and `_CRT_DECLARE_NONSTDC_NAMES=1`.
- Sets the module type to `kernelmodedriver`, imports `ntoskrnl` and `hal`, and uses `inc/ext2fs.h` as the precompiled header.
- Installs the driver into `reactos/system32/drivers` and registers `ext2fs_reg.inf`.

Build invariants:
- The driver vendors or directly builds many Linux-like compatibility sources and NLS tables into one kernel driver target.
- GNU and Clang warning suppressions indicate the code intentionally relies on pointer-sign conversions, unused functions/variables, packed-member addresses, and other compatibility patterns.

Filesystem/build relevance:
- This is the complete ReactOS build recipe for the bundled Ext2Fsd-derived ext2/ext3/ext4 filesystem driver.

Notable risks:
- `add_definitions()` applies the listed definitions directory-wide rather than only to `ext2fs`.
- The large static source list means adding/removing Ext2Fsd components requires manual CMake maintenance.
