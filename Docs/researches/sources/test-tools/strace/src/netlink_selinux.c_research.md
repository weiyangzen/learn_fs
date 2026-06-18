<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_selinux.c -->
# sources/test-tools/strace/src/netlink_selinux.c

Purpose: decodes SELinux netlink notification payloads.

Important APIs/types/functions: `decode_netlink_selinux`, `struct selnl_msg_setenforce`, and `struct selnl_msg_policyload`.

Control flow: switches on `SELNL_MSG_SETENFORCE` and `SELNL_MSG_POLICYLOAD`, printing `val` or `seqno` respectively; unknown message types return false so the main netlink layer prints raw payload.

State and persistence behavior: no persistent state.

Dependencies and integration points: called by `netlink.c` for `NETLINK_SELINUX`; depends on `<linux/selinux_netlink.h>`.

Risks: only two SELinux message payload shapes are decoded. Future SELinux netlink messages require new cases.

Test signals: setenforce and policyload netlink messages, short payloads, unknown SELinux message types, and fetch failures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_selinux.c -->
