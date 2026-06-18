# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt09.c

## Purpose
Check for possible double free of rx_owner_map after switching packet interface versions aka
CVE-2021-22600. Kernel crash fixed in: commit ec6af094ea28f0f2dda1a6a33b14cd57e36a9755 Author:
Willem de Bruijn <willemb@google.com> Date: Wed Dec 15 09:39:37 2021 -0500 net/packet: rx_owner_map
depends on pg_vec commit c800aaf8d869f2b9b47b10c5c312fe19f0a94042 Author: WANG Cong
<xiyou.wangcong@gmail.com> Date: Mon Jul 24 10:07:32 2017 -0700 packet: fix use-after-free in
prb_retire_rx_blk_timer_expired(). CVE/regression focus: CVE-2021-22600. Referenced kernel commit
ids include `ec6af094ea28f0f2dda1a6a33b14cd57e36a9755`, `c800aaf8d869f2b9b47b10c5c312fe19f0a94042`,
`ec6af094ea28`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct tpacket_req3`,
`struct tst_test`, `struct tst_path_val`, `struct tst_tag`; constants/macros `TPACKET_V3`,
`TPACKET_ALIGNMENT`, `AF_PACKET`, `SOL_PACKET`, `PACKET_VERSION`, `PACKET_RX_RING`, `TPACKET_V2`;
safe wrappers `SAFE_SYSCONF`, `SAFE_SOCKET`, `SAFE_SETSOCKOPT`, `SAFE_SETSOCKOPT_INT`, `SAFE_CLOSE`;
harness APIs `tst_test`, `tst_setup_netns`, `TEST`, `tst_brk`, `tst_taint_check`, `tst_res`,
`tst_path_val`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `setup`, `run`, `cleanup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, kernel config gates "CONFIG_USER_NS=y",
"CONFIG_NET_NS=y". The file is built by the syscall directory Makefile and executed as part of the
LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; missing kernel options cause configuration skips rather than
failures; signal and timeout based assertions depend on scheduler timing.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status
values `EINVAL`; regression tags for CVE-2021-22600.
