<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/274 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/274

## Purpose
This fixture verifies RCU stall parsing for IPv6 receive handling on a compat writev/tun input path. The expected title is `INFO: rcu detected stall in ipv6_rcv`, alt `stall in ipv6_rcv`, and type `HANG`.

## Important APIs, Types, and Functions
The raw log contains an `rcu_sched self-detected stall on CPU` and a deep IPv6 receive stack. Parser paths include RCU stall matching, NMI/IRQ stack skipping, and network frame selection. Important symbols include `__sanitizer_cov_trace_pc`, `__xfrm_decode_session`, `__xfrm_policy_check`, `ip6_input_finish`, `ip6_input`, `ip6_mc_input`, `ip6_rcv_finish`, `ipv6_rcv`, `__netif_receive_skb_core`, `tun_rx_batched.isra.50`, `tun_get_user`, `tun_chr_write_iter`, `compat_writev`, and `entry_SYSENTER_compat`.

## Control Flow
The reporter processes RCU timer and NMI frames, then extracts the stalled network receive stack. It must title at `ipv6_rcv`, not xfrm policy helpers, tun ingress helpers, or compat syscall wrappers.

## State and Persistence Behavior
The fixture stores expected HANG metadata and raw log data. There is no mutable state or persistence outside the checked-in file.

## Dependencies and Integration Points
It depends on Linux RCU stall regexes, network-stack frame prioritization, and hang alternate-title generation.

## Risks and Edge Cases
The stack includes many plausible network frames and a 32-bit compat syscall tail. Title selection must remain stable across these details.

## Test Signals
The parse must return `INFO: rcu detected stall in ipv6_rcv`, alt `stall in ipv6_rcv`, and type `HANG`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/274 -->
