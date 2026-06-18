<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_devlink_cmd.in -->
# sources/test-tools/strace/src/xlat/genl_devlink_cmd.in

Purpose: Declarative xlat input table `genl_devlink_cmd` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 85 constant rows, including `DEVLINK_CMD_UNSPEC`
- Representative constants: `DEVLINK_CMD_UNSPEC`, `DEVLINK_CMD_GET`, `DEVLINK_CMD_SET`, `DEVLINK_CMD_NEW`, `DEVLINK_CMD_DEL`, `DEVLINK_CMD_PORT_GET`, `DEVLINK_CMD_PORT_SET`, `DEVLINK_CMD_PORT_NEW`, `DEVLINK_CMD_PORT_DEL`, `DEVLINK_CMD_PORT_SPLIT`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/devlink.h`, `#Prefix DEVLINK_CMD_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_devlink_cmd.in -->
