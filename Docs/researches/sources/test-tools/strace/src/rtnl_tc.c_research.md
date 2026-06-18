# sources/test-tools/strace/src/rtnl_tc.c

Purpose: Decodes traffic-control route-netlink messages (`tcmsg`) and common qdisc/class/filter stats attributes.

Important APIs/types/functions: `decode_tcmsg`, exported `decode_nla_tc_stats`, `decode_tc_stats`, `decode_tc_estimator`, `decode_gnet_stats_*`, and `decode_tca_stab`.

Control flow: fixed `tcmsg` prints family, ifindex, handle, parent, and info, then attributes. `TCA_STATS` decodes old `tc_stats`; `TCA_STATS2` decodes nested gnet stats; `TCA_STAB` decodes size spec and uint16 table arrays.

State and persistence: stateless.

Dependencies/integration: Linux `gen_stats.h`, `pkt_sched.h`, rtnetlink, nlattr helpers, xlat tables for TC attrs/stats/stab. `rtnl_tc_action.c` reuses the `decode_nla_tc_stats` exported decoder.

Risks: many `TCA_OPTIONS`/`TCA_XSTATS` payloads are subsystem-specific and intentionally unimplemented here. Length validation for old stats uses `offsetofend` for portable minimums.

Test signals: qdisc/class/filter netlink messages with kind, old stats, stats2 basic/rate/queue/rate64, stab data, chain/block attrs, malformed short stats.
