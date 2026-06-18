<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fib_rule_actions.in -->
# sources/test-tools/strace/src/xlat/fib_rule_actions.in

Purpose: Declarative xlat input table `fib_rule_actions` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 9 constant rows, including `FR_ACT_UNSPEC`
- Representative constants: `FR_ACT_UNSPEC`, `FR_ACT_TO_TBL`, `FR_ACT_GOTO`, `FR_ACT_NOP`, `FR_ACT_RES3`, `FR_ACT_RES4`, `FR_ACT_BLACKHOLE`, `FR_ACT_UNREACHABLE`, `FR_ACT_PROHIBIT`
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/fib_rules.h`, `#Prefix FR_ACT_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/fib_rule_actions.in -->
