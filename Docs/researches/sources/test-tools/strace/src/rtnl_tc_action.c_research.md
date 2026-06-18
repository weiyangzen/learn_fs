# sources/test-tools/strace/src/rtnl_tc_action.c

Purpose: Decodes traffic-control action route-netlink messages and root/action nested attributes.

Important APIs/types/functions: action attr decoders `decode_tca_action`, `decode_tca_root_act_tab`, `decode_tca_act_flags`, `decode_tca_act_hw_stats`, `decode_tca_msecs`, and root attr tables.

Control flow: root action tables misuse nesting as an array, so the decoder invokes `decode_nlattr` with a single action decoder and no xlat table. Each action decodes kind, index, stats, cookie/default payload, flags, hardware stats, and in-hardware count. Root attrs decode flags and optional time intervals as milliseconds.

State and persistence: stateless.

Dependencies/integration: Linux `pkt_cls.h`/rtnetlink, `rtnl_tc.c` stats decoder, xlat tables for action attrs/root flags/hw stats, and nlattr framework.

Risks: `TCA_ACT_OPTIONS` is action-specific and unimplemented here. Root table's nonstandard nesting requires careful generic decoder setup. Millisecond values can be shorter than u64 and are widened by helper.

Test signals: TC action dump/new/del messages with multiple actions, stats, flags, hardware stats, cookie payloads, root flags, msecs attrs, and malformed nested arrays.
