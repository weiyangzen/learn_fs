# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt07.c

## Purpose
CVE-2017-1000111 Check for race condition between packet_set_ring() and tp_reserve. The race allows
you to set tp_reserve bigger than ring buffer size. While this will cause truncation of all incoming
packets to 0 bytes, sanity checks in tpacket_rcv() prevent any exploitable buffer overflows. Race
fixed in v4.13 c27927e372f0 ("packet: fix tp_reserve race in packet_set_ring"). CVE/regression
focus: CVE-2017-1000111. Referenced kernel commit ids include `c27927e372f0`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct tst_fzsync_pair`,
`struct tpacket_req3`, `struct tst_test`, `struct tst_path_val`, `struct tst_tag`; constants/macros
`SOL_PACKET`, `PACKET_RESERVE`, `TPACKET_V3`, `AF_PACKET`, `PACKET_VERSION`, `PACKET_RX_RING`; safe
wrappers `SAFE_SYSCONF`, `SAFE_SOCKET`, `SAFE_GETSOCKOPT`, `SAFE_CLOSE`; harness APIs `tst_test`,
`tst_fuzzy_sync`, `tst_fzsync_pair`, `tst_setup_netns`, `tst_fzsync_pair_init`, `tst_fzsync_run_b`,
`tst_fzsync_start_race_b`, `tst_fzsync_end_race_b`, `tst_fzsync_pair_reset`, `tst_fzsync_run_a`,
`TEST`, `tst_brk`, `tst_fzsync_start_race_a`, `tst_fzsync_end_race_a`.

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
reports success by not crashing; race reproduction is timing-sensitive and can be flaky on slow or
heavily loaded systems; missing kernel options cause configuration skips rather than failures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status
values `EINVAL`; regression tags for CVE-2017-1000111.
