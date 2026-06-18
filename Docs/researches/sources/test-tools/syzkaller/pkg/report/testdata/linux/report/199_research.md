<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/199 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/199

## Purpose
This fixture validates KASAN stack-out-of-bounds read parsing in iterator advancement while handling TUN input. Expected title is `KASAN: stack-out-of-bounds Read in iov_iter_advance`, alt `bad-access in iov_iter_advance`, and type `KASAN-READ`.

## Important APIs, Types, And Functions
The 165-line log includes allocation failure noise, netfilter setup frames, and the KASAN stack-out-of-bounds report. Important frames include `iov_iter_advance`, `tun_get_user`, `tun_chr_write_iter`, `dump_stack`, `warn_alloc_failed`, `__vmalloc_node_range`, `vmalloc`, `xt_alloc_entry_offsets`, `translate_table`, `do_arpt_set_ctl`, `nf_setsockopt`, `ip_setsockopt`, `tcp_setsockopt`, `sock_common_setsockopt`, and `SyS_setsockopt`.

## Control Flow
The reporter should find the KASAN stack-out-of-bounds line and title the report from `iov_iter_advance`, not from preceding allocation/netfilter noise. Runtime flow for the primary bug is write into a TUN character device, which advances an iov iterator and triggers the sanitizer read.

## State And Persistence
Persistent state is title, alt, type, and raw log. Dynamic stack addresses, allocation failures, TUN packet data, and syscall arguments are volatile. The fixture is static.

## Dependencies And Integration Points
It depends on KASAN stack-out-of-bounds parsing, noisy-prefix filtering, and TUN/VFS stack extraction. It integrates as a Linux report parser test case for sanitizer reports embedded in unrelated console activity.

## Risks
Potential regressions include selecting `tun_get_user` instead of `iov_iter_advance`, choosing allocation failure as the report, or losing the `KASAN-READ` type.

## Test Signals
Assert title `KASAN: stack-out-of-bounds Read in iov_iter_advance`, alt `bad-access in iov_iter_advance`, and type `KASAN-READ`. The selected text should include the TUN write path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/199 -->
