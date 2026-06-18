<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_nlctrl.c -->
# sources/test-tools/strace/src/netlink_nlctrl.c

Purpose: specialized decoder for the generic netlink controller (`nlctrl`) family, including family metadata, operations, multicast groups, and policy descriptions.

Important APIs/types/functions: `decode_nlctrl`, `family_names`, `decode_nla_ctrl_attr_family_name`, operation and policy nested decoders, and xlat mappings for known generic families such as devlink, ethtool, ioam6, mptcp_pm, netdev, nl80211, taskstats, tcp_metrics, and thermal.

Control flow: prints `genlmsghdr` command/version/reserved, then decodes `CTRL_ATTR_*` attributes. The family-name attribute updates an opaque index so operation ids can be rendered with the family-specific command table, including send/receive tables for ethtool.

State and persistence behavior: no global state; a per-message `family_names_idx` is passed through nested attribute decoding.

Dependencies and integration points: called from `netlink_generic.c`; uses `nlattr` nested decoding and many generated generic-family xlat tables.

Risks: semantic command rendering depends on seeing `CTRL_ATTR_FAMILY_NAME` before nested operation attributes and on the hardcoded family-name table staying current. Unknown policy attributes fall back to raw output.

Test signals: cover `CTRL_CMD_*` messages with family names, ops, mcast groups, policy and op-policy nests, ethtool receive/send command rendering, unknown families, and missing family-name ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_nlctrl.c -->
