<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/aio_cmds.in -->
# sources/test-tools/strace/src/xlat/aio_cmds.in

Purpose: Declarative xlat input table `aio_cmds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 9 constant rows, including `IOCB_CMD_PREAD		0`
- Representative constants: `IOCB_CMD_PREAD`, `IOCB_CMD_PWRITE`, `IOCB_CMD_FSYNC`, `IOCB_CMD_FDSYNC`, `IOCB_CMD_PREADX`, `IOCB_CMD_POLL`, `IOCB_CMD_NOOP`, `IOCB_CMD_PREADV`, `IOCB_CMD_PWRITEV`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/aio_abi.h`, `#Prefix IOCB_CMD_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/aio_cmds.in -->
