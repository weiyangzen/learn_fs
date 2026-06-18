# sources/security-integrity/fscrypt/metadata/checks.go

## Purpose
`checks.go` defines validation for all metadata protobuf structures before they are persisted or trusted after reading from disk.

## Important APIs, Types, and Functions
`Metadata` combines `CheckValidity` and `proto.Message`. `CheckValidity` methods exist for `EncryptionOptions_Mode`, `SourceType`, `HashingCosts`, `WrappedKeyData`, `ProtectorData`, `EncryptionOptions`, `WrappedPolicyKey`, `PolicyData`, and `Config`. `MaxParallelism` constrains Argon2 parallelism.

## Control Flow
Validation rejects default or unknown enums, nil messages, invalid Argon2 cost ranges, invalid salt/IV/HMAC/key/descriptor lengths, missing source-specific fields, bad padding, and unsupported policy versions. `EncryptionOptions.CheckValidity` normalizes unset policy version `0` to `1` for legacy compatibility. `HashingCosts` preserves backwards compatibility by truncating old overlarge parallelism when `TruncationFixed` is false and the uint8 truncation is nonzero.

## State and Persistence
Validation mutates `EncryptionOptions.PolicyVersion` from `0` to `1` and may log truncation behavior. It otherwise reads in-memory protobuf structs. Its results gate filesystem persistence and loaded metadata trust.

## Dependencies and Integration Points
Depends on metadata constants, `util.CheckValidLength`, padding arrays from `policy.go`, protobuf interfaces, and `github.com/pkg/errors`. `filesystem.addMetadata`, `filesystem.getMetadata`, config loading, and policy setup rely on these checks.

## Risks
Validation is a security boundary for disk metadata. Backward-compatible parallelism truncation is intentional but can surprise operators reading old metadata. Because `CheckValidity` mutates policy version, callers should not assume it is pure.

## Test Signals
`filesystem_test.go`, `config_test.go`, and `policy_test.go` exercise many validation failures: bad source, missing hashing costs, wrong wrapped key lengths, bad descriptor lengths, invalid padding/modes, and legacy config policy-version normalization.
