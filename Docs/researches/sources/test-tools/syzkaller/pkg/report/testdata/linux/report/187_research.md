<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/187 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/187

## Purpose
This fixture verifies lockdep parsing for an IPv4 getsockopt path. Expected title is `possible deadlock in do_ip_getsockopt`, type `LOCKDEP`. It ensures read-side socket option paths are not folded into the setsockopt titles used by nearby fixtures.

## Important APIs, Types, And Functions
The file is a static lockdep report fixture. Important parser concepts include circular-dependency detection, stack owner selection, and function normalization. Key frames include `do_ip_getsockopt`, `rtnl_lock`, `__mutex_lock`, `mutex_lock_nested`, `unregister_netdevice_notifier`, `clusterip_tg_destroy`, `cleanup_entry`, `__do_replace`, `do_ipt_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, `SyS_setsockopt`, `xt_find_table_lock`, `xt_request_find_table_lock`, and `get_info`.

## Control Flow
The reporter should detect the first lockdep warning and derive title from the `do_ip_getsockopt` stack. The runtime path includes getsockopt and netfilter table information lookup interacting with a previously described CLUSTERIP teardown lock chain.

## State And Persistence
The fixture persists 145 lines of lockdep text and the expected metadata. Lockdep object addresses and task details are volatile. There is no executable state or side effect in the repository.

## Dependencies And Integration Points
It depends on syzkaller's Linux lockdep parser and title heuristics for socket option accessors. Integration is the common testdata loop over `pkg/report/testdata/linux/report`.

## Risks
The parser may choose `rtnl_lock` or an xtables helper instead of `do_ip_getsockopt`, or it may conflate this getsockopt regression with setsockopt fixtures. Missing dependency-chain boundaries can also change report text.

## Test Signals
The title must remain `possible deadlock in do_ip_getsockopt` with `LOCKDEP` type. The report should preserve both the getsockopt stack and the lock chain through netfilter/CLUSTERIP cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/187 -->
