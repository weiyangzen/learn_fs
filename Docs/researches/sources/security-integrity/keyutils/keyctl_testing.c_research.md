<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl_testing.c -->
# sources/security-integrity/keyutils/keyctl_testing.c

## Purpose

`keyctl_testing.c` adds hidden `keyctl --test` subcommands for probing kernel key type, description, and user payload limits. These routines are used by the feature limit tests rather than by normal users.

## Important APIs, Types, and Functions

`test_commands[]` maps `limits` and `limits2` to `act_keyctl_test_limits()` and `act_keyctl_test_limits2()`. `act_keyctl_test()` delegates through shared `do_command()`. `act_keyctl_test_limits()` varies key type and description lengths, expecting invalid type errors or valid user-key creation within size limits. `act_keyctl_test_limits2()` iterates payload sizes up to just over 1 MiB, expecting user-type payload acceptance only for 1..32767 bytes while tolerating transient `EDQUOT`.

## Control Flow

The top-level test command validates a subcommand and dispatches it. Each limit test runs a loop, prints progress markers to stdout, creates keys on the thread keyring, unlinks any successful temporary key, counts unexpected outcomes, and aborts early after too many failures.

## State and Persistence Behavior

Temporary keys are created in `KEY_SPEC_THREAD_KEYRING` and unlinked immediately when creation succeeds. Local buffers carry candidate type/description/payload content. No filesystem state is written by this module.

## Dependencies and Integration Points

The file uses `add_key()` and `keyctl_unlink()` from libkeyutils, `KEY_SPEC_THREAD_KEYRING`, and command dispatch declarations from `keyctl.h`. `tests/features/limits/runtest.sh` is the main integration point.

## Risks and Edge Cases

The loops are intentionally heavy and can hit quota races; `limits2` treats `EDQUOT` as acceptable for fast key creation. Kernel-version behavior differs on older MIPS kernels, so external tests gate part of the run. The static payload buffer is large and stack-allocated.

## Test Signals

Pass signals are zero exit status from `keyctl --test limits` and `keyctl --test limits2`, with no unexpected errno values and no leaked temporary keys in the thread keyring.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl_testing.c -->
