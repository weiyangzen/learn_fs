<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/186 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/186

## Purpose
This is the IPv6 counterpart to the previous lockdep fixture. It expects title `possible deadlock in do_ipv6_setsockopt` and type `LOCKDEP`, covering circular locking during IPv6 socket option processing.

## Important APIs, Types, And Functions
The test fixture uses `TITLE` and `TYPE` headers plus a raw Linux lockdep trace. Important parser behavior is lockdep warning detection, IPv6 function naming despite inlined suffixes, and separation of dependency stacks. Important frames include `do_ipv6_setsockopt.isra.8`, `rtnl_lock`, `__mutex_lock`, `mutex_lock_nested`, `unregister_netdevice_notifier`, `clusterip_tg_destroy`, `cleanup_entry`, `__do_replace`, `do_ipt_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, `SyS_setsockopt`, and xtables lookup functions.

## Control Flow
The parser scans the circular locking warning and builds a lockdep report. The runtime flow begins with IPv6 setsockopt, crosses protocol socket option dispatch, and reaches netfilter table replacement and CLUSTERIP cleanup where RTNL and xtables locks interact. The expected title should prefer `do_ipv6_setsockopt` from the active stack.

## State And Persistence
The persistent content is a 155-line golden lockdep log and expected type. Lock instances, task names, addresses, and generated suffixes such as `.isra.8` are volatile and must be normalized or ignored appropriately.

## Dependencies And Integration Points
It integrates with syzkaller's Linux lockdep parsing and netfilter stack handling. It depends on frame normalization that can keep the semantic function name while tolerating compiler-generated suffixes.

## Risks
This fixture can regress if the parser confuses IPv4 and IPv6 paths or chooses a helper lock function as title. Because it resembles report 185, dedup or title logic must not collapse both cases to the same title.

## Test Signals
Checks should assert `possible deadlock in do_ipv6_setsockopt`, type `LOCKDEP`, and presence of the IPv6 setsockopt frame plus CLUSTERIP cleanup lock chain.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/186 -->
