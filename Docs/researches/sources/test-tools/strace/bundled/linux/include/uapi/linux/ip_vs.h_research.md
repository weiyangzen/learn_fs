# sources/test-tools/strace/bundled/linux/include/uapi/linux/ip_vs.h

Purpose: exposes IP Virtual Server userspace ABI for configuring virtual services, real destinations, sync daemons, timeouts, and statistics through legacy socket options and generic netlink.

Important APIs/types/functions: legacy structures include `ip_vs_service_user`, `ip_vs_dest_user`, `ip_vs_stats_user`, `ip_vs_getinfo`, `ip_vs_service_entry`, `ip_vs_dest_entry`, `ip_vs_get_dests`, `ip_vs_get_services`, `ip_vs_timeout_user`, and `ip_vs_daemon_user`. Netlink enums define `IPVS_CMD_*`, service/destination/daemon/stat/info attributes, and `ip_vs_flags`.

Control flow: tools create/edit/delete services and destinations, read lists and stats, start/stop sync daemons, set timeouts, flush state, and zero counters. Legacy setsockopt/getsockopt numbers coexist with the generic netlink family `IPVS`.

State/persistence behavior: configuration changes persistent kernel load-balancer state; stats and counters change with traffic and may be reset. Sync daemon state persists until stopped or namespace teardown.

Dependencies/integration: depends on Linux fixed-width and big-endian types. Integrates with netfilter/conntrack, scheduler modules, tunnel encapsulation, multicast sync, and userspace tools such as `ipvsadm`.

Risks and test signals: several structs contain flexible arrays or fixed-size names. Tests should cover socket option decoding, nested generic netlink service/dest attributes, stats64 variants, tunnel flags, fwmark-vs-address service selection, and counter reset commands.
