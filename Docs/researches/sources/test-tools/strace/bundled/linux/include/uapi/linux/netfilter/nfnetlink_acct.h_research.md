# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_acct.h

Purpose: defines nfnetlink accounting object ABI for named packet/byte counters, quotas, quota notifications, filtering, and counter-zeroing reads.

Important APIs/types/functions: exports `NFACCT_NAME_MAX`, message types `NFNL_MSG_ACCT_*`, quota flags `NFACCT_F_QUOTA_PKTS`, `BYTES`, `OVERQUOTA`, attributes for name, packets, bytes, use count, flags, quota, filter, and filter mask/value attributes.

Control flow: userspace creates/gets/deletes accounting objects, reads counters with or without reset, receives over-quota notifications, and can filter dumps by mask/value.

State/persistence behavior: accounting objects are persistent per-netns netfilter state. Packet/byte counters update with matching traffic, quota state can transition to overquota, and get-ctrzero mutates counters by clearing them.

Dependencies/integration: uses nfnetlink subsystem `NFNL_SUBSYS_ACCT` and integrates with nftables/iptables expressions that reference accounting objects.

Risks and test signals: counter-zeroing reads have side effects and overquota is kernel-set only. Tests should decode all message types, quota flags, name limits, filter nesting, and get-vs-get-reset behavior.
