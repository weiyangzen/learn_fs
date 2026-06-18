# sources/security-integrity/fscrypt/actions/context.go

## Purpose
Defines the action-layer `Context`, the high-level state object tying together config, mount, target user, and metadata trust policy for protector and policy operations.

## APIs, Types, and Control Flow
`Context` contains `Config`, `Mount`, `TargetUser`, and optional `TrustedUser`. `NewContextFromPath` resolves the mount containing a path; `NewContextFromMountpoint` resolves a specific mountpoint. Both call `newContextFromUser`, which defaults to `util.EffectiveUser`, loads config, and sets `TrustedUser` to the effective user for non-root callers unless cross-user metadata is allowed.

`checkContext` validates config and filesystem setup. `getKeyringOptions` projects context into `keyring.Options`. `getProtectorOption` loads protector metadata, detecting linked protectors by comparing returned mount with the context mount. `ProtectorOptions` lists descriptors and converts them into options with per-option load errors.

## State, Dependencies, and Integration
Context is read-mostly state, but it controls all later persistence through `filesystem.Mount`, filtering by `TrustedUser`, and keyring behavior through `keyring.Options`. It integrates config loading, mount discovery, user identity, and metadata ownership constraints.

## Risks and Test Signals
The trusted-user rule is a security boundary for non-root metadata reads. Mount equality is pointer/value sensitive and affects linked protector reporting. `context_test.go` builds a real test context and validates that a config file is required before context creation.
