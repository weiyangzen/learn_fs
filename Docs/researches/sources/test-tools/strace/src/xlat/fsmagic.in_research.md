<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsmagic.in -->
# sources/test-tools/strace/src/xlat/fsmagic.in

Purpose: Declarative xlat input table `fsmagic` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 117 constant rows, including `QNX4_SUPER_MAGIC	0x0000002f`
- Representative constants: `QNX4_SUPER_MAGIC`, `Z3FOLD_MAGIC`, `AUTOFS_SUPER_MAGIC`, `DEVFS_SUPER_MAGIC`, `EXT_SUPER_MAGIC`, `MINIX_SUPER_MAGIC`, `MINIX_SUPER_MAGIC2`, `DEVPTS_SUPER_MAGIC`, `MINIX2_SUPER_MAGIC`, `MINIX2_SUPER_MAGIC2`...
- Generator directives/preprocessor guards: `#sorted sort -k2,2`, `#From fs/befs/befs_fs_types.h`, `#From fs/freevxfs/vxfs.h`, `#From fs/hfs/hfs.h`, `#From fs/hfsplus/hfsplus_raw.h`, `#From fs/jfs/jfs_incore.h`, `#From fs/ubifs/ubifs.h`, `#From fs/ufs/ufs_fs.h`...

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fsmagic.in -->
