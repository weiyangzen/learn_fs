<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/188 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/188

## Purpose
This fixture checks lockdep parsing when the selected title is the lock acquisition function itself: `possible deadlock in rtnl_lock`, type `LOCKDEP`. The trace covers circular locking between rtnetlink and IPv6/xtables socket option paths.

## Important APIs, Types, And Functions
The static fixture exposes syzkaller's lockdep parser to a 181-line dependency report. Important frames include `rtnl_lock`, `xt_find_table_lock`, `__mutex_lock`, `mutex_lock_nested`, `xt_find_revision`, `do_ip6t_get_ctl`, `nf_getsockopt`, `ipv6_getsockopt`, `tcp_getsockopt`, `sock_common_getsockopt`, `SyS_getsockopt`, `lock_sock_nested`, `do_ipv6_setsockopt.isra.8`, `ipv6_setsockopt`, `rawv6_setsockopt`, `sock_common_setsockopt`, and `SyS_setsockopt`.

## Control Flow
The Linux reporter enters at the circular-lock warning and parses multiple stack sections. Unlike the preceding socket-option fixtures, the expected owner is `rtnl_lock`, indicating that the active dependency evidence points at RTNL lock acquisition itself. The parser must not force every netfilter lockdep report to a syscall wrapper title.

## State And Persistence
Persistent state is the expected title and type plus raw lockdep text. Dynamic kernel addresses, lock class ids, task ids, and CPU ids are volatile. The fixture has no runtime mutation.

## Dependencies And Integration Points
It integrates with Linux lockdep matching and netfilter/IPv6 title heuristics. It depends on syzkaller preserving dependency graph text sufficiently for stable parsing of the selected culprit.

## Risks
Risk lies in over-normalizing the title to `do_ip6t_get_ctl` or `do_ipv6_setsockopt`, which would lose the intended RTNL focus. Another risk is truncating one of the two stack sections and changing selection.

## Test Signals
Expected signal is exact title `possible deadlock in rtnl_lock` and type `LOCKDEP`. The output should include xtables getsockopt frames and raw IPv6 setsockopt frames, showing the conflicting acquisition paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/188 -->
