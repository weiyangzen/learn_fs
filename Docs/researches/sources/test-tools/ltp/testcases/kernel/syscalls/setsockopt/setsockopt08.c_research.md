# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt08.c

## Purpose
This will reproduce the bug on x86_64 in 32bit compatibility mode. It is most reliable with KASAN
enabled. Otherwise it relies on the out-of-bounds write corrupting something which leads to a crash.
It will run in other scenarious, but is not a test for the CVE. See
https://google.github.io/security-research/pocs/linux/cve-2021-22555/writeup.html Also below is
Nicolai's detailed description of the bug itself. The problem underlying CVE-2021-22555 fixed by
upstream commit b29c457a6511 ("netfilter: x_tables: fix compat match/target pad out-of-bound write")
is that the (now removed) padding zeroing code in xt_compat_target_from_user() had been based on the
premise that the user specified. CVE/regression focus: CVE-2021-22555. Referenced kernel commit ids
include `b29c457a6511`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct compat_ipt_replace`,
`struct xt_entry_target`, `struct ipt_replace`, `struct ipt_entry`, `struct xt_entry_match`, `struct
tst_test`, `struct tst_buffers`, `struct tst_path_val`, `struct tst_tag`; constants/macros
`AF_INET`; safe wrappers `SAFE_SOCKET`, `SAFE_CLOSE`; harness APIs `tst_test`, `tst_safe_net`,
`tst_is_compat_mode`, `tst_res`, `tst_setup_netns`, `TEST`, `tst_brk`, `tst_buffers`,
`tst_path_val`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.forks_child`. Local functions include `setup`, `run`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, kernel config gates
"CONFIG_NETFILTER_XT_MATCH_STATE", "CONFIG_IP_NF_TARGET_REJECT", "CONFIG_USER_NS=y",
"CONFIG_NET_NS=y". The file is built by the syscall directory Makefile and executed as part of the
LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; compatibility-mode behavior depends on architecture, compiler
flags, and kernel ABI support; missing kernel options cause configuration skips rather than
failures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TCONF`, `TINFO`, `TTERRNO`, `TERRNO`; expected errno/status
values `ENOPROTOOPT`, `EINVAL`; regression tags for CVE-2021-22555.
