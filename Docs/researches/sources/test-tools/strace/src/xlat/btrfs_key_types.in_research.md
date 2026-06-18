<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_key_types.in -->
# sources/test-tools/strace/src/xlat/btrfs_key_types.in

Purpose: Declarative xlat input table `btrfs_key_types` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 46 constant rows, including `BTRFS_INODE_ITEM_KEY`
- Representative constants: `BTRFS_INODE_ITEM_KEY`, `BTRFS_INODE_REF_KEY`, `BTRFS_INODE_EXTREF_KEY`, `BTRFS_XATTR_ITEM_KEY`, `BTRFS_VERITY_DESC_ITEM_KEY`, `BTRFS_VERITY_MERKLE_ITEM_KEY`, `BTRFS_ORPHAN_ITEM_KEY`, `BTRFS_DIR_LOG_ITEM_KEY`, `BTRFS_DIR_LOG_INDEX_KEY`, `BTRFS_DIR_ITEM_KEY`...
- Generator directives/preprocessor guards: `#sorted`, `#val_type uint64_t`, `#From include/linux/libfdt_env.h`, `#From include/uapi/linux/btrfs_tree.h`, `#Prefix BTRFS_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/btrfs_key_types.in -->
