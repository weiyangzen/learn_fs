# File Research: sources/local-fs/apfs-fuse/CMakeLists.txt

This CMake file defines the apfs-fuse build. It requires CMake 3.0, names the project `Apfs`, enables C99 and C++11, sets Release build type, and adds `-Wall -Wextra` to C and C++ flags. It includes the project root and bundled `3rdparty/lzfse/src`.

It declares an option `USE_FUSE3` defaulting ON. For Linux/non-Apple FUSE builds, this chooses between linking `fuse3` and linking `fuse` with `USE_FUSE2` defined.

The build creates three libraries. `lzfse` is built from bundled Apple LZFSE/LZVN C sources. `crypto` is built from local AES, AES-XTS, ASN.1 DER, crypto, DES, SHA-1, SHA-256, and Triple-DES sources. `apfs` is the main library and includes container, directory, node mapping, volume, dumping, B-tree, checkpoint map, CRC32, decompression, device backends, disk image formats, GPT partition map, key management, plist, utility, and Unicode sources.

`apfs` links against `z`, `bz2`, `lzfse`, and `crypto`, and publicly defines `_FILE_OFFSET_BITS=64` and `_DARWIN_USE_64_BIT_INODE`. These definitions are important for large-file support and Darwin inode behavior.

The file defines four executables: `apfs-dump`, `apfs-dump-quick`, `apfs-fuse`, and `apfsutil`. `apfs-fuse` links to OSXFUSE directly on Apple using `/usr/local/lib/libosxfuse.dylib`; otherwise it links to FUSE2 or FUSE3 depending on the option. Install rules install `apfs-fuse` and `apfsutil` into the runtime bindir.

Notable build constraints: dependency discovery is manual rather than using `find_package` for zlib, bzip2, or FUSE. The hard-coded OSXFUSE include/library path may need local adjustment on modern macOS systems.
