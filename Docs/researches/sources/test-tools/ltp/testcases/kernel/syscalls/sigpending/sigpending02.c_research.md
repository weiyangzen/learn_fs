# sources/test-tools/ltp/testcases/kernel/syscalls/sigpending/sigpending02.c

## Purpose
AUTHORS Paul Larson Matthias Maennich Test 1: Suppress handling SIGUSR1 and SIGUSR1, raise them and
assert their signal pending. Test 2: Call sigpending(sigset_t*=-1), it should return -1 with errno
EFAULT.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `sigemptyset`, `sigaddset`, `signal`,
`sigpending`, `sigprocmask`; types `struct tst_test`; constants/macros `SIGUSR1`, `SIGSETSIZE`,
`SIGMAX`, `SIGUSR2`, `SIG_SETMASK`; safe wrappers `SAFE_SIGNAL`; harness APIs `tst_test`,
`tst_variant`, `tst_res`, `tst_brk`, `tst_syscall`, `TEST`, `tst_get_bad_addr`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`,
`.test_variants`. Local functions include `sigpending_info`, `tested_sigpending`, `sighandler`,
`test_sigpending`, `test_efault_on_invalid_sigset`, `run`.

## State and persistence behavior
The test changes per-process signal dispositions, masks, pending queues, or alternate signal stack
state. State is scoped to the LTP process tree unless a privileged syscall changes host-visible
kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/syscalls.h` compatibility wrappers. The
file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery; obsolete or direct
syscall paths may be absent or emulated differently on newer architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TINFO`, `TTERRNO`, `TERRNO`; expected
errno/status values `EFAULT`.
