# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt02.c

## Purpose
Test for CVE-2017-7308 on a raw socket's ring buffer Try to set tpacket_req3.tp_sizeof_priv to a
value with the high bit set. So that tp_block_size < tp_sizeof_priv. If the vulnerability is present
then this will cause an integer arithmetic overflow and the absurd tp_sizeof_priv value will be
allowed. If it has been fixed then setsockopt will fail with EINVAL. We also try a good
configuration to make sure it is not failing with EINVAL for some other reason. For a better and
more interesting discussion of this CVE see:
https://googleprojectzero.blogspot.com/2017/05/exploiting-linux-kernel-via-packet.html.
CVE/regression focus: CVE-2017-7308.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct tpacket_req3`,
`struct tst_test`, `struct tst_tag`; constants/macros `TPACKET_V3`, `AF_PACKET`, `SOL_PACKET`,
`PACKET_VERSION`, `PACKET_RX_RING`; safe wrappers `SAFE_SYSCONF`, `SAFE_CLOSE`, `SAFE_SOCKET`;
harness APIs `tst_test`, `tst_safe_net`, `TEST`, `tst_brk`, `tst_res`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_root`. Local functions include `setup`, `cleanup`, `create_skbuf`,
`good_size`, `bad_size`, `run`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; privilege assumptions can produce `TCONF`/`TBROK` instead of
meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TTERRNO`, `TERRNO`; expected errno/status
values `EINVAL`; regression tags for CVE-2017-7308.
