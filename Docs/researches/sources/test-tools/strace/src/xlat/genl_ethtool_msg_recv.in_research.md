<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ethtool_msg_recv.in -->
# sources/test-tools/strace/src/xlat/genl_ethtool_msg_recv.in

Purpose: Declarative xlat input table `genl_ethtool_msg_recv` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 55 constant rows, including `ETHTOOL_MSG_KERNEL_NONE`
- Representative constants: `ETHTOOL_MSG_KERNEL_NONE`, `ETHTOOL_MSG_STRSET_GET_REPLY`, `ETHTOOL_MSG_LINKINFO_GET_REPLY`, `ETHTOOL_MSG_LINKINFO_NTF`, `ETHTOOL_MSG_LINKMODES_GET_REPLY`, `ETHTOOL_MSG_LINKMODES_NTF`, `ETHTOOL_MSG_LINKSTATE_GET_REPLY`, `ETHTOOL_MSG_DEBUG_GET_REPLY`, `ETHTOOL_MSG_DEBUG_NTF`, `ETHTOOL_MSG_WOL_GET_REPLY`...
- Generator directives/preprocessor guards: `#unconditional`, `#value_indexed`, `#From include/uapi/linux/ethtool_netlink_generated.h`, `#Prefix ETHTOOL_MSG_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/genl_ethtool_msg_recv.in -->
