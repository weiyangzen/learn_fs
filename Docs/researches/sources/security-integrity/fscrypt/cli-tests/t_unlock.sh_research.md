# sources/security-integrity/fscrypt/cli-tests/t_unlock.sh

## Purpose
Tests unlocking encrypted directories and metadata corruption failures.

## Control Flow and Integration
Encrypts with `--skip-unlock`, checks locked status and mount policy row, unlocks and creates data, cycles the mount to lock again, verifies wrong passphrase failure, unlocks successfully, corrupts policy metadata and expects unlock failure, then tests missing policy metadata, missing protector metadata, and swapped policy metadata between two directories.

## State and Risks
Directly edits `.fscrypt/policies` and `.fscrypt/protectors` to simulate corruption. Exercises `GetPolicyFromPath`, metadata mismatch detection, bad config/protector load errors, and keyring provisioning.

## Test Signals
Strong negative coverage for integrity between kernel policy data and fscrypt metadata.
