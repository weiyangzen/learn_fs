# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/443

Purpose: golden fixture for Linux 4.4 hung-task parsing where the title is `INFO: task hung in rtnl_lock`, alternate title is `hang in rtnl_lock`, and type is `HANG`.

Important APIs, types, and functions: the syzkaller parser APIs are `ParseTest` headers and Linux report extraction. The kernel stacks cover `rtnl_lock`, `ipv6_route_ioctl`, `inet6_ioctl`, `sock_do_ioctl`, `sock_ioctl`, `do_vfs_ioctl`, plus multiple `proc_cleanup_work` workers in `synchronize_sched`, perf release paths, `tun_chr_close`, and `ipv6_sock_mc_close`.

Control flow: after header parsing, the reporter sees a primary blocked ioctl path holding `rtnl_mutex`. The file then includes other blocked workqueue and executor stacks, including compact `<Same stack as pid ...>` markers. The correct flow is to identify the first hung-task report and preserve the title frame from the route ioctl path.

State and persistence behavior: static golden data stores a noisy multi-task hung-task snapshot. The fixture persists older kernel formatting, including 4.4-style task lines and `<Same stack as pid>` summaries.

Dependencies and integration points: depends on compatibility with older Linux console formatting and lock-debug output. It integrates IPv6 route ioctl, proc namespace cleanup, perf teardown, and tun close hangs into one parser stress fixture.

Risks: repeated stacks and abbreviated stack references can confuse report end detection. If parser selection prefers later repeated stacks, title may become `synchronize_sched`, `perf_trace_destroy`, or `tun_chr_close` instead of `rtnl_lock`.

Test signals: `INFO: task syz-executor.4:15720 blocked`, frame `ipv6_route_ioctl+0x1f8/0x2b0`, held `rtnl_mutex`, workqueue `events proc_cleanup_work`, and several `<Same stack as pid ...>` lines.
