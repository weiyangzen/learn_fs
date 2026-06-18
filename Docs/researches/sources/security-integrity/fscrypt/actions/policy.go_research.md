# sources/security-integrity/fscrypt/actions/policy.go

## Purpose
Implements fscrypt policy lifecycle: create, load, apply, unlock, provision, deprovision, add/remove protectors, and purge keys. A policy represents a directory encryption key plus metadata describing its wrapped copies and encryption options.

## APIs, Types, and Control Flow
Error types cover access denied on unsupported v2 kernels, already protected, filesystem mismatch, missing metadata, not protected, removing the only protector, and metadata mismatch. `PurgeAllPolicies` lists policies on a mount and removes their keys from keyrings while tolerating absent keys and logging partial-removal cases.

`Policy` stores context, metadata, in-memory key, creation flag, owner for metadata creation, and linked protectors created during cross-filesystem attachment. `CreatePolicy` generates a random policy key, computes a v1 or v2 descriptor, creates metadata from context options, determines metadata owner for login protectors, and calls `AddProtector`. `GetPolicy` loads mount metadata by descriptor. `GetPolicyFromPath` reads kernel policy from the path, maps encryption support errors, detects likely unsupported-v2 permission denial, loads stored metadata, and verifies descriptor/options match.

Unlocking occurs either through `Unlock`, which selects a protector option and unwraps via callback-derived protector key, or `UnlockWithProtector`, which uses an already-unlocked protector. `AddProtector` requires both keys unlocked, creates linked protector metadata when mounts differ, wraps the policy key with the protector key, appends metadata, and commits. `RemoveProtector` removes a wrapped key unless it is the last one. `Apply` enforces same filesystem before calling `metadata.SetPolicy`. Provisioning and deprovisioning proxy to `keyring`.

## State, Dependencies, and Integration
Persistent state lives in `.fscrypt/policies` and linked `.fscrypt/protectors` through `filesystem.Mount`. Kernel state lives in user or filesystem keyrings via `keyring`. Crypto wrapping uses `crypto.Wrap` and `Unwrap`; metadata comparison uses protobuf equality.

## Risks and Test Signals
Rollback is mostly in-memory: failed commits restore wrapped-key lists, and created policies can be reverted by callers. Cross-filesystem links are cleanup-sensitive via `newLinkedProtectors`. `RemoveProtector` intentionally does not preserve wrapped-key order. Tests cover creation, duplicate additions, removal failures, callback unlock, direct protector unlock, and locked-protector rejection. CLI tests add coverage for corrupt/missing metadata, v1 behavior, and lock/unlock integration.
