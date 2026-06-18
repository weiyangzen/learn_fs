# sources/security-integrity/fscrypt/cmd/fscrypt/commands.go

## Purpose
Defines the fscrypt CLI command tree and implements user-facing workflows by orchestrating `actions`, keyring, filesystem, metadata, and prompt helpers.

## APIs, Types, and Control Flow
Top-level commands are `Setup`, `Encrypt`, `Unlock`, `Lock`, `Purge`, `Status`, and `Metadata`. `setupAction` creates global config and root metadata or sets up a specified filesystem. `encryptAction` delegates to `encryptPath`, then chmods encrypted directories to `0700` and prints locked/unlocked result. `encryptPath` parses target user, creates context, validates empty/encryptable directory, selects or creates a policy/protector, validates keyring prerequisites, optionally creates recovery passphrase, unlocks/provisions as needed, applies the policy, and writes recovery instructions. Deferred cleanup reverts newly created protectors/policies on error.

`validateKeyringPrereqs` enforces v1 user-keyring or filesystem-keyring requirements. `unlockAction` loads the path policy, validates keyring access, rejects already-unlocked state, unlocks the policy, and provisions it. `lockAction` deprovisions keys, maps keyring partial-removal errors to CLI errors, and uses v1 heuristics plus optional cache dropping. `purgeAction` confirms and removes all policy keys from a mount. `statusAction` dispatches global, mountpoint, or path status. Metadata subcommands create/destroy protectors and policies, change passphrases, add/remove protectors from policies, and dump debug metadata.

## State, Dependencies, and Integration
This file is the main integration layer. It mutates global config, `.fscrypt` metadata, directory policy xattrs, file modes, kernel keyrings, kernel caches, and recovery files. It depends on action objects for durable metadata semantics and command helpers for prompts, flags, errors, and formatting.

## Risks and Test Signals
The most important risks are cleanup correctness when multi-step encryption fails, destructive metadata commands, v1 keyring permission logic, and partial lock semantics. CLI tests in this subset exercise setup, encrypt variants, lock/unlock, metadata, status, v1 modes, and error suggestions.
