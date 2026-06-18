# sources/test-tools/strace/src/rtnl_rule.c

Purpose: Decodes FIB rule route-netlink messages and attributes.

Important APIs/types/functions: `decode_fib_rule_hdr`, `decode_rule_addr`, `decode_fib_rule_uid_range`, `decode_rule_port_range`, and rule attr decoder table.

Control flow: fixed header prints family, dst/src lengths, tos, table, action, and flags, then attrs. Address attrs use header family; UID and port ranges decode fixed start/end structs.

State and persistence: stateless.

Dependencies/integration: Linux `fib_rules.h`, netlink/nlattr helpers, xlat tables for rule attrs/actions/flags, routing table IDs.

Risks: field names and action/table semantics overlap with route headers but use distinct xlat tables. Short range attrs must be rejected safely.

Test signals: IPv4/IPv6 rule messages with src/dst, fwmark, table, uid range, sport/dport ranges, action/flags, malformed attrs.
