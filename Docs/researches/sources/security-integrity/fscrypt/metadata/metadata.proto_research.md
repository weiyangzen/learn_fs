# sources/security-integrity/fscrypt/metadata/metadata.proto

## Purpose
`metadata.proto` is the authoritative schema for fscrypt metadata stored in `.fscrypt` files and for the global JSON config.

## Important APIs, Types, and Functions
Messages define hashing costs, wrapped keys, protectors, encryption options, wrapped policy keys, policies, and config. Enums define protector source types and encryption modes corresponding to kernel fscrypt mode constants. The `compatibility` field number and name are reserved.

## Control Flow
There is no runtime control flow. Schema changes require running `make gen` to regenerate `metadata.pb.go`.

## State and Persistence
Field numbers define persistent wire compatibility. `ProtectorData` stores source, optional passphrase hashing settings, salt, UID, and wrapped internal key. `PolicyData` stores key descriptor, encryption options, and wrapped policy-key slots. `Config` stores defaults and behavior flags.

## Dependencies and Integration Points
The Go package option maps generated code to `github.com/google/fscrypt/metadata`. The schema is consumed by filesystem metadata persistence, crypto wrapping, config JSON, actions, keyring selection, and PAM login protector discovery.

## Risks
Changing field numbers or enum values would break compatibility with existing metadata. Adding new encryption modes must be matched with validation and kernel support logic. Reserved fields protect legacy configs from accidental reuse.

## Test Signals
Config, filesystem, policy, and generated-code usage tests indirectly validate that the schema matches expected JSON and protobuf behavior.
