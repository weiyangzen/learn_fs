<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/caif_protocols.in -->
# sources/test-tools/strace/src/xlat/caif_protocols.in

Purpose: Declarative xlat input table `caif_protocols` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 6 constant rows, including `CAIFPROTO_AT		0`
- Representative constants: `CAIFPROTO_AT`, `CAIFPROTO_DATAGRAM`, `CAIFPROTO_DATAGRAM_LOOP`, `CAIFPROTO_UTIL`, `CAIFPROTO_RFM`, `CAIFPROTO_DEBUG`
- Generator directives/preprocessor guards: `#value_indexed`, `#From include/uapi/linux/caif/caif_socket.h`, `#Prefix CAIFPROTO_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/caif_protocols.in -->
