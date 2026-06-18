# sources/security-integrity/fscrypt/actions/recovery.go

## Purpose
Adds automatic recovery passphrase support for login-protected directories on non-root filesystems, allowing access if root-filesystem login protector metadata is lost.

## APIs, Types, and Control Flow
`modifiedContextWithSource` clones a context and config with a different protector source. `AddRecoveryPassphrase` generates a 20-character random passphrase, creates a custom-passphrase protector named `Recovery passphrase for <dirname>` with numeric suffixes on collisions, adds it to the policy, and returns both the passphrase key and protector. On add failure it reverts the created protector.

`WriteRecoveryInstructions` opens a new no-follow `0600` file, writes human-readable instructions including the recovery passphrase, protector identifier, and removal command, optionally chowns it to the metadata owner, and fsyncs it.

## State, Dependencies, and Integration
This code persists an additional protector and updates policy metadata. It uses `proto.Clone` to avoid mutating the original context config, `crypto.NewRandomPassphrase`, and `util.Chown`. The CLI `encryptPath` calls this when a login protector is on a different mount and `--no-recovery` is not set.

## Risks and Test Signals
The recovery file contains plaintext recovery secret by design and must be protected by directory encryption plus mode `0600`. Name collision handling can loop until an available name is found. Tests verify length, default and collision names, policy protector count, unlockability, and file contents.
