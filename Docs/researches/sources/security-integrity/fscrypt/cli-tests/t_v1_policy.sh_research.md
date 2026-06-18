# sources/security-integrity/fscrypt/cli-tests/t_v1_policy.sh

## Purpose
Tests deprecated v1 encryption policies using the user keyring.

## Control Flow and Integration
Sets up a clean session keyring, edits config to policy version 1, verifies root and invalid user-keyring scenarios fail, encrypts as test user, checks status as user and root, creates files, verifies user/root locking restrictions, locks with `--user`, tests incomplete lock detection with an open file, and finishes locking.

## State and Risks
Exercises user keyring access, session keyring linkage, v1 status heuristics, and root/user permission distinctions. Requires keyctl behavior to match assumptions.

## Test Signals
Critical compatibility coverage for older policy/keyring mode and partial-lock heuristics.
