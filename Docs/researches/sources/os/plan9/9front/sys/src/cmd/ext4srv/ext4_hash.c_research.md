# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_hash.c

Directory hash implementation for ext2/ext3/ext4 htree indexed directories. It implements the legacy, TEA, and half-MD4 hash variants used by ext directory indexing, including signed and unsigned character modes.

Key behavior:
- Defines local MD4 round macros and `ext2_half_md4`, derived from the RSA MD4 transform but reduced to the half-MD4 form Linux uses for htree directory names.
- Implements `ext2_tea` for the TEA htree hash variant.
- Implements `ext2_legacy_hash` for the older signed/unsigned legacy hash.
- `ext2_prep_hashbuf` packs filename bytes into 32-bit words with length-derived padding, using signed or unsigned character interpretation depending on hash version.
- `ext2_htree_hash` validates the name and hash version, optionally applies a superblock hash seed, computes major/minor hashes, clears the low collision bit, avoids the EOF sentinel, and reports unsupported versions via `werrstr`.

Notable dependencies:
- Hash version constants and `EXT2_HTREE_EOF` are declared in `include/ext4_types.h`.
- Used by indexed directory code through `include/ext4_hash.h` and `ext4_dir_idx.c`.
- Relies on Plan 9-style `werrstr` for error reporting.

Research notes:
- Names must be 1..255 bytes; empty names and overlong names fail.
- The implementation mutates `name`/`len` while processing hash chunks, so callers only receive the final major/minor values.
- The major hash low bit is reserved for htree collision continuation, matching ext directory-index conventions.
