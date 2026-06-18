# File Research: sources/windows/reactos/drivers/filesystems/btrfs/CMakeLists.txt

Build definition for the ReactOS Btrfs kernel-mode filesystem driver, derived from WinBtrfs sources.

Key behavior:
- Adds include paths for ReactOS driver headers, ReactOS zlib headers, and the local `inc` directory.
- Defines the vendored Zstandard source list used by Btrfs compression support.
- Builds a `btrfs` module from the main Btrfs driver sources, checksum/hash sources, compression helpers, IOCTL/control paths, cache/free-space handling, tree/extent logic, send/scrub/security/reparse support, and `btrfs_drv.h`.
- Adds architecture-specific assembly helpers `crc32c.S` and `xor.S` for i386 and amd64.
- Creates `btrfs` as a kernel-mode driver module with `set_module_type(btrfs kernelmodedriver)`.
- Links against `rtlver`, `zlib_solo`, `chkstk`, `wdmguid`, `${PSEH_LIB}`, and imports `ntoskrnl` plus `hal`.
- Installs the driver under `reactos/system32/drivers`, adds `btrfs.inf`, and registers `btrfs_reg.inf`.

Build invariants:
- `__KERNEL__` is globally defined for this target.
- MSVC warning C4267 is suppressed for this driver.
- Zstd is built from in-tree C files rather than as an external package target.

Filesystem/build relevance:
- This file is the complete ReactOS build recipe for the Btrfs filesystem driver and shows that Btrfs support is compiled as a loadable kernel filesystem module with bundled compression/hash code.

Notable risks:
- The target embeds multiple third-party or imported components directly, including WinBtrfs-derived code, BLAKE2, zlib integration, and Zstd sources.
- Architecture-specific assembly is enabled only on x86/x64; other architectures fall back to C implementations where available.
