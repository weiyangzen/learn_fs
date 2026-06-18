<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bluetooth_l2_cid.in -->
# sources/test-tools/strace/src/xlat/bluetooth_l2_cid.in

Purpose: Declarative xlat input table `bluetooth_l2_cid` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 10 constant rows, including `L2CAP_CID_SIGNALING	0x0001`
- Representative constants: `L2CAP_CID_SIGNALING`, `L2CAP_CID_CONN_LESS`, `L2CAP_CID_A2MP`, `L2CAP_CID_ATT`, `L2CAP_CID_LE_SIGNALING`, `L2CAP_CID_SMP`, `L2CAP_CID_SMP_BREDR`, `L2CAP_CID_DYN_START`, `L2CAP_CID_LE_DYN_END`, `L2CAP_CID_DYN_END`
- Generator directives/preprocessor guards: `#sorted sort -k2,2`, `#From include/net/bluetooth/l2cap.h`, `#Prefix L2CAP_CID_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bluetooth_l2_cid.in -->
