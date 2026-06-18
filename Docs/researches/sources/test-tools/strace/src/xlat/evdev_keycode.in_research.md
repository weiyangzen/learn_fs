<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_keycode.in -->
# sources/test-tools/strace/src/xlat/evdev_keycode.in

Purpose: Declarative xlat input table `evdev_keycode` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as: awk '{if (NF>1) {n=strtonum($2)}; printf("%d %s\n", n, $0)}' |sort -s -k1,1n |sed 's/^[0-9]* //'

Important APIs/types/functions:
- Contains 627 constant rows, including `KEY_RESERVED`
- Representative constants: `KEY_RESERVED`, `KEY_ESC`, `KEY_1`, `KEY_2`, `KEY_3`, `KEY_4`, `KEY_5`, `KEY_6`, `KEY_7`, `KEY_8`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/input-event-codes.h`, `#Prefix BTN_ KEY_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/evdev_keycode.in -->
