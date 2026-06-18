# sources/security-integrity/fscrypt/cli-tests/t_v1_policy_fs_keyring.sh

## Purpose
Tests deprecated v1 policies configured to use the filesystem keyring.

## Control Flow and Integration
Edits config to enable `use_fs_keyring_for_v1_policies` and policy version 1. Verifies user encrypt without skip-unlock fails, user encrypt with `--skip-unlock` succeeds but remains locked, user unlock/lock fails, root unlock and lock succeed, and user can read when root has unlocked.

## State and Risks
Exercises `NeedsRootToProvision`, `ErrFsKeyringPerm`, v1 policy application without provisioning, and shared filesystem-keyring visibility.

## Test Signals
Validates the special v1 fs-keyring mode used for compatibility with newer kernel mechanisms.
