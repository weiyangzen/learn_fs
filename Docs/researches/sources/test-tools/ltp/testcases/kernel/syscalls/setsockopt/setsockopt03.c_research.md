# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt03.c

## Purpose
Test for CVE-2016-4997 For a full explanation of how the vulnerability works see:
https://github.com/nccgroup/TriforceLinuxSyscallFuzzer/tree/master/crash_reports/report_compatIpt
The original vulnerability was present in the 32-bit compatibility system call, so the test should
be compiled with -m32 and run on a 64-bit kernel. For simplicities sake the test requests root
privileges instead of creating a user namespace. CVE/regression focus: CVE-2016-4997. Referenced
kernel commit ids include `ce683e5f9d04`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`; types `struct ipt_entry`, `struct
xt_entry_match`, `struct xt_entry_target`, `struct payload`, `struct ipt_replace`, `struct
tst_test`, `struct tst_tag`; constants/macros `AF_INET`, `SOL_IP`; safe wrappers `SAFE_SOCKET`;
harness APIs `tst_test`, `tst_safe_net`, `tst_kernel`, `tst_is_compat_mode`, `tst_res`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test_all`,
`.test`, `.needs_root`. Local functions include `setup`, `run`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; compatibility-mode behavior depends on architecture, compiler
flags, and kernel ABI support; privilege assumptions can produce `TCONF`/`TBROK` instead of
meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TINFO`, `TERRNO`; regression tags for CVE-2016-4997.
