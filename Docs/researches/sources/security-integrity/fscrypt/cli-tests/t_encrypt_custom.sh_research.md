# sources/security-integrity/fscrypt/cli-tests/t_encrypt_custom.sh

## Purpose
Tests encryption using custom passphrase protectors.

## Control Flow and Integration
Runs non-interactive encryption with `--name=prot`, interactive encryption selecting custom passphrase source and name, and a negative case where quiet custom protector creation lacks a name.

## State and Risks
Exercises `promptForSource`, `promptForName`, `makeKeyFunc`, `CreateProtector`, `CreatePolicy`, and status output. Prompt text changes can break expected output.

## Test Signals
Validates both flag-driven and prompt-driven custom passphrase flows, plus required-name enforcement.
