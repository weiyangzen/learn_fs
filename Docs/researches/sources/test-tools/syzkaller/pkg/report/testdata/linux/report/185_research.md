<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/185 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/185

## Purpose
This fixture validates lockdep circular-dependency parsing for IPv4 setsockopt. The expected title is `possible deadlock in do_ip_setsockopt` and type `LOCKDEP`. The log starts with `WARNING: possible circular locking dependency detected`.

## Important APIs, Types, And Functions
The fixture is report parser data; headers drive expected metadata. Parser logic under test includes lockdep title extraction, held-lock/dependency block boundary handling, and choosing the syscall-side top frame. Important functions include `do_ip_setsockopt.isra.12`, `rtnl_lock`, `__mutex_lock`, `mutex_lock_nested`, `unregister_netdevice_notifier`, `clusterip_tg_destroy`, `cleanup_entry`, `__do_replace`, `do_ipt_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, `SyS_setsockopt`, `xt_find_table_lock`, `xt_request_find_table_lock`, and `get_info`.

## Control Flow
The Linux reporter detects the lockdep warning and parses the dependency chain. The runtime path is a user `setsockopt` call entering IPv4 netfilter table replacement, where CLUSTERIP cleanup interacts with RTNL locking and xtables locks. The title should reflect `do_ip_setsockopt`, not the helper `rtnl_lock`.

## State And Persistence
The file persists a 153-line lockdep report and expected metadata. Lock addresses, lock class names, and task ids are transient data. No state is mutated by the fixture except parser test expectations.

## Dependencies And Integration Points
It depends on Linux lockdep report regexes, stack-frame extraction, and crash-type mapping to `LOCKDEP`. It integrates through the syzkaller Linux report test suite and overlaps with netfilter/CLUSTERIP warning fixtures in this group.

## Risks
Lockdep traces contain multiple stacks; the parser could select the wrong side of the dependency, generating `possible deadlock in rtnl_lock` or `clusterip_tg_destroy`. Report-boundary handling must not discard dependency details needed for title selection.

## Test Signals
Exact title and type are the primary signal. The report should include circular dependency text and both the `do_ip_setsockopt` and CLUSTERIP/netfilter cleanup stack segments.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/185 -->
