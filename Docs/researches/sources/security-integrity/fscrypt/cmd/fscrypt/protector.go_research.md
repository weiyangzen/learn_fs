# sources/security-integrity/fscrypt/cmd/fscrypt/protector.go

## Purpose
Command-layer helper for creating and selecting protectors, especially ensuring login protectors live on the configured root mount.

## APIs, Types, and Control Flow
`createProtectorFromContext` prompts for source and name, requires `--user` when root creates login protectors, shows login setup warning, switches context to `LoginProtectorMountpoint` for login protectors, sets owner to target user when root, and calls `actions.CreateProtector`. `selectExistingProtector` prompts and loads a protector from an option. `expandedProtectorOptions` returns protectors on the current mount plus root login protectors not already seen, marking them as linked options. `modifiedContext` clones a context with mount replaced by `LoginProtectorMountpoint`.

## State, Dependencies, and Integration
Bridges CLI prompt/flag behavior with action protector creation and filesystem mount discovery. It controls cross-filesystem linked protector availability for encryption.

## Risks and Test Signals
Root login-protector creation without explicit user is rejected to avoid accidentally using root credentials. Linked option setup is subtle: root options are returned as selectable for non-root mounts. CLI login encryption tests cover these behaviors.
