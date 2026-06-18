# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt05.c

## Purpose
CVE-2017-1000112 Check that UDP fragmentation offload doesn't cause memory corruption if the
userspace process turns off UFO in between two send() calls. Kernel crash fixed in 4.13 85f1bd9a7b5a
("udp: consistently apply ufo or fragmentation"). CVE/regression focus: CVE-2017-1000112. Referenced
kernel commit ids include `85f1bd9a7b5a`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `send`; types `struct sockaddr_in`, `struct
ifreq`, `struct sockaddr`, `struct tst_test`, `struct tst_path_val`, `struct tst_tag`;
constants/macros `AF_INET`, `SIOCSIFMTU`, `SIOCSIFFLAGS`, `SOL_SOCKET`, `SO_NO_CHECK`; safe wrappers
`SAFE_SOCKET`, `SAFE_IOCTL`, `SAFE_BIND`, `SAFE_GETSOCKNAME`, `SAFE_CLOSE`, `SAFE_CONNECT`,
`SAFE_SEND`, `SAFE_SETSOCKOPT_INT`; harness APIs `tst_test`, `tst_net`, `tst_setup_netns`,
`tst_init_sockaddr_inet_bin`, `tst_taint_check`, `tst_res`, `tst_path_val`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `setup`, `cleanup`, `run`.

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
failures.

## Test signals
LTP result macros `TPASS`, `TFAIL`; regression tags for CVE-2017-1000112.
