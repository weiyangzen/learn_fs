
# sources/security-integrity/ima-evm-utils/tests/Makefile.am

## Purpose
This automake fragment defines the top-level ima-evm-utils test scripts, optional kernel-test subdirectory, cleanup behavior, log display helper, shellcheck target, and key cleanup hook.

## Important APIs, Types, And Functions
It populates `check_SCRIPTS` and `TESTS`, adds `kernel` to `SUBDIRS` when `KERNEL_TESTS` is enabled, and declares `ima_hash.test`, `sign_verify.test`, `boot_aggregate.test`, and `ima_policy_check.test`. Phony targets include `check_logs`, `shellcheck`, and `distclean-keys`.

## Control Flow
Automake runs scripts listed in `TESTS`. `check_logs` prints selected log tails for long hash/sign logs and full logs for others, then delegates to the kernel subdir. Cleanup removes generated signatures/output text and calls `gen-keys.sh clean`.

## State And Persistence
Generated test artifacts include `.txt`, `.out`, `.sig`, `.sig2`, and key material created by `gen-keys.sh`. Distclean removes generated keys and CA config.

## Dependencies And Integration Points
The file integrates tests with automake and shellcheck, and conditionally includes kernel-level tests that require a suitable kernel/securityfs environment.

## Risks
`check_logs` always calls `make -C kernel $@`, so builds without generated kernel makefiles or with disabled subdirs may need automake context. Test scripts depend on system capabilities such as xattrs, OpenSSL algorithms, TPM helpers, and IMA policy access.

## Test Signals
This file is itself the test signal inventory for top-level userspace functionality.
