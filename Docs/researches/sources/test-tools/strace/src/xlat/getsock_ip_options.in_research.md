<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/getsock_ip_options.in -->
# sources/test-tools/strace/src/xlat/getsock_ip_options.in

Purpose: Declarative xlat input table `getsock_ip_options` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as:  Options specific to getsockopt(SOL_IP).

Important APIs/types/functions:
- Contains 20 constant rows, including `ARPT_SO_GET_INFO`
- Representative constants: `ARPT_SO_GET_INFO`, `ARPT_SO_GET_ENTRIES`, `ARPT_SO_GET_REVISION_MATCH`, `ARPT_SO_GET_REVISION_TARGET`, `EBT_SO_GET_INFO`, `EBT_SO_GET_ENTRIES`, `EBT_SO_GET_INIT_INFO`, `EBT_SO_GET_INIT_ENTRIES`, `IP_VS_SO_GET_VERSION`, `IP_VS_SO_GET_INFO`...
- Generator directives/preprocessor guards: `#From include/uapi/linux/ip_vs.h`, `#From include/uapi/linux/netfilter_arp/arp_tables.h`, `#From include/uapi/linux/netfilter_bridge/ebtables.h`, `#From include/uapi/linux/netfilter_ipv4/ip_tables.h`, `#Prefix ARPT_SO_GET_ EBT_SO_GET_ IP_VS_SO_GET_ IPT_SO_GET_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/getsock_ip_options.in -->
