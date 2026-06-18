# File Research: sources/windows/reactos/sdk/lib/fslib/btrfslib/CMakeLists.txt

Read completely: 19 lines.

This build file creates `btrfslib`. It adds the Btrfs driver source include directory, compiles shared Btrfs checksum/hash sources (`blake2b-ref.c`, `crc32c.c`, `sha256.c`, `xxhash.c`) plus `btrfslib.c`, and adds architecture-specific CRC32C assembly for i386/amd64 through `add_asm_files`.

It defines `_USRDLL` privately for the target and depends on `psdk`. The library reuses driver headers and checksum implementations rather than carrying separate format-library copies.

Security/reliability notes: no runtime behavior. Build correctness depends on driver header compatibility and architecture-specific assembly availability.
