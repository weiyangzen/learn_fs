# sources/security-integrity/fscrypt/cli-tests/t_not_enabled.sh

## Purpose
Tests behavior when an ext4 filesystem supports encryption but the encryption feature is disabled, then tests enabling it.

## Control Flow and Integration
Disables the ext4 encrypt feature with `debugfs`, remounts, verifies global enabled count decreases, checks encrypt/unlock/lock fail, checks extra GRUB warning when `/boot/grub` appears on the filesystem, enables encryption with `tune2fs -O encrypt`, and verifies encryption succeeds.

## State and Risks
Mutates filesystem feature flags on loopback devices and relies on ext4 tools. It drives error suggestions from `errors.go`, especially GRUB and enablement guidance.

## Test Signals
Strong signal for support/enabled distinction and remediation messages.
