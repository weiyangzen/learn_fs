# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_cttimeout.h

Purpose: defines nfnetlink ABI for named conntrack timeout policies and protocol-specific timeout values.

Important APIs/types/functions: exports timeout message types for new/get/delete/default set/default get, top-level attrs `CTA_TIMEOUT_*`, protocol timeout attr groups for generic, TCP, UDP, UDPLite, ICMP, DCCP, SCTP, ICMPv6, GRE, and `CTNL_TIMEOUT_NAME_MAX`.

Control flow: userspace creates or queries timeout policy objects by name/L3/L4 protocol, provides nested per-protocol timeout data, deletes policies, or reads/sets protocol defaults.

State/persistence behavior: timeout policy objects and defaults are persistent per-netns conntrack configuration and influence expiration of future/live conntrack entries depending on attachment.

Dependencies/integration: includes `nfnetlink.h`; integrates with conntrack, nftables ct timeout objects, and helper/expectation behavior.

Risks and test signals: protocol-specific nested attr interpretation changes with L4 protocol. Tests should decode every protocol timeout enum, default set/get messages, name limits, use counts, and unused/deprecated SCTP heartbeat-acked value.
