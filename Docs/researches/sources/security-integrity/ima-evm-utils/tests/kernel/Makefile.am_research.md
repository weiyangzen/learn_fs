
# sources/security-integrity/ima-evm-utils/tests/kernel/Makefile.am

## Purpose
This automake fragment defines kernel-facing ima-evm-utils tests and a small C helper program.

## Important APIs, Types, And Functions
When `KERNEL_TESTS` is enabled, `TESTS` is set to `check_SCRIPTS`. Listed scripts include `fsverity.test`, `portable_signatures.test`, `mmap_check.test`, `evm_hmac.test`, `non_action_rule_flags.test`, and `creds_check.test`. `check_PROGRAMS := test_mmap` builds the mmap helper.

## Control Flow
Automake builds `test_mmap` and runs the script tests. `check_logs` prints full logs. Cleanup removes generated text/output/signature artifacts and delegates key cleanup to `../gen-keys.sh clean`.

## State And Persistence
Tests may create xattrs, temporary files, signed policy files, and generated keys. The makefile cleanup removes only local generated artifacts.

## Dependencies And Integration Points
It integrates the top-level test harness with kernel securityfs, IMA/EVM policy, keyrings, fs-verity, and mmap behavior.

## Risks
Kernel tests require privileged operations and suitable kernel config. Running them on a host with an existing IMA policy can be disruptive unless policy overlap checks work correctly.

## Test Signals
This file declares the kernel-level validation surface for portable signatures, fs-verity signatures, HMAC, policy rule flags, creds, and mmap hooks.
