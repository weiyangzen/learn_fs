# sources/test-tools/strace/src/rtnl_neightbl.c

Purpose: Decodes neighbor table configuration/statistics route-netlink messages (`ndtmsg`).

Important APIs/types/functions: `decode_ndtmsg`, `decode_ndta_parms`, `decode_ndt_config`, `decode_ndt_stats`, and `ndt_parms_nla_decoders`.

Control flow: prints family, then decodes `NDTA_*` attrs. Parameters and stats are nested/fixed structures with many timing/count fields; stats accept either minimum or full struct size.

State and persistence: stateless.

Dependencies/integration: Linux neighbor table UAPI, xlat tables for `NDTA_*`/`NDTPA_*`, nlattr helpers.

Risks: variable stats size needs exact min/full handling. Timer units are printed as raw u64 by current decoders, so semantic conversions depend on shared helpers where used.

Test signals: neighbor table dump with config, parms, stats min/full lengths, GC interval, and malformed short stats.
