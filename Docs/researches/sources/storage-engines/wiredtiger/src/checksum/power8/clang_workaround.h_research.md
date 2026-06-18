<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/clang_workaround.h -->
# sources/storage-engines/wiredtiger/src/checksum/power8/clang_workaround.h

## Purpose
Provides compatibility wrappers that let the POWER8 vector CRC implementation compile under Clang despite differences from GCC vector builtins and historical `vec_xxpermdi` behavior.

## Important APIs, Types, and Functions
The header maps missing `__builtin_crypto_vpmsumw` and `__builtin_crypto_vpmsumd` to `__builtin_crypto_vpmsumb`, defines an overloadable `vec_ld` wrapper using `__builtin_altivec_lvx`, provides `__builtin_pack_vector`, and provides `__builtin_unpack_vector_0` and, when `REFLECT` is not defined, `__builtin_unpack_vector_1`. For older Clang or missing `vec_xxpermdi`, unpacking uses vector indexing with endian-aware macros; newer Clang uses `vec_xxpermdi`.

## Control Flow
This is a compile-time adaptation layer. `vec_crc32.c` includes it only when `__clang__` is defined. Preprocessor branches select big-endian versus little-endian packing order and older versus newer Clang unpack implementations.

## State and Persistence Behavior
The header has no runtime state or persistence. It affects checksum persistence indirectly by ensuring Clang-built POWER8 CRC code performs the same vector lane packing and unpacking as the GCC path.

## Dependencies and Integration Points
It depends on AltiVec vector types and Clang/GCC-compatible builtin names. It is tightly coupled to `vec_crc32.c`, especially the reflected CRC mode controlled by `REFLECT` from `crc32_constants.h`.

## Risks and Edge Cases
Endian handling is delicate: incorrect lane order would silently generate incompatible CRC values. The fallback mapping of vpmsum builtins assumes Clang accepts the byte builtin for the required vector polynomial operations. Clang version checks around `vec_xxpermdi` are compatibility-sensitive; future compiler changes could require updating this header.

## Test Signals
POWER8 builds with Clang should pass the generic CRC tests. `wt2695_checksum` is particularly important because it compares hardware/vector output with software output for known values, random chunks, cumulative seeded checksums, and 0-15 byte misalignment patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/checksum/power8/clang_workaround.h -->
