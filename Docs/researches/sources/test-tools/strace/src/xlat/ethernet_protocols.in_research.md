<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ethernet_protocols.in -->
# sources/test-tools/strace/src/xlat/ethernet_protocols.in

Purpose: Declarative xlat input table `ethernet_protocols` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 101 constant rows, including `ETH_P_802_3	0x0001		/* Dummy type for 802.3 frames  */`
- Representative constants: `ETH_P_802_3`, `ETH_P_AX25`, `ETH_P_ALL`, `ETH_P_802_2`, `ETH_P_SNAP`, `ETH_P_DDCMP`, `ETH_P_WAN_PPP`, `ETH_P_PPP_MP`, `ETH_P_LOCALTALK`, `ETH_P_CAN`...
- Generator directives/preprocessor guards: `#sorted sort -k2,2`, `#From include/uapi/linux/if_ether.h`, `#Prefix ETH_P_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/ethernet_protocols.in -->
