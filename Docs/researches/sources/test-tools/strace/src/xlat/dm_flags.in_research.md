<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/dm_flags.in -->
# sources/test-tools/strace/src/xlat/dm_flags.in

Purpose: Declarative xlat input table `dm_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 19 constant rows, including `DM_READONLY_FLAG`
- Representative constants: `DM_READONLY_FLAG`, `DM_SUSPEND_FLAG`, `DM_EXISTS_FLAG`, `DM_PERSISTENT_DEV_FLAG`, `DM_STATUS_TABLE_FLAG`, `DM_ACTIVE_PRESENT_FLAG`, `DM_INACTIVE_PRESENT_FLAG`, `DM_BUFFER_FULL_FLAG`, `DM_SKIP_BDGET_FLAG`, `DM_SKIP_LOCKFS_FLAG`...
- Generator directives/preprocessor guards: `#unconditional`, `#From include/uapi/linux/dm-ioctl.h`, `#Prefix DM_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/dm_flags.in -->
