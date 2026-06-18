# sources/security-integrity/fscrypt/cmd/fscrypt/flags.go

## Purpose
Defines all CLI flags, custom flag types, and helpers for parsing metadata identifiers and users.

## APIs, Types, and Control Flow
Custom `boolFlag`, `durationFlag`, and `stringFlag` implement `cli.Flag` plus formatting accessors used by help output. `allFlags` feeds formatting width computation and `universalFlags` adds verbose, quiet, and help everywhere. Flags include setup time, source, name, key file, user, protector, unlock-with, policy, force, skip-unlock, drop-caches, all-users, and no-recovery.

`matchMetadataFlag` parses `MOUNTPOINT:ID` via regex. `parseMetadataFlag` creates a context for that mountpoint. `getProtectorFromFlag` and `getPolicyFromFlag` load locked metadata objects. `parseUserFlag` returns explicit user or effective user.

## State, Dependencies, and Integration
Flag structs are package globals whose `Value` fields are populated by `urfave/cli`. They drive command behavior, prompt defaults, key collection, metadata lookup, and target user selection.

## Risks and Test Signals
Global mutable flags make tests and repeated invocations in one process sensitive to stale values, though the CLI process normally exits after one command. The metadata flag regex accepts printable mountpoints and alnum descriptors only. CLI tests cover many flag combinations.
