# sources/security-integrity/fscrypt/metadata/config.go

## Purpose
`config.go` serializes and deserializes the global fscrypt config protobuf as human-readable JSON.

## Important APIs, Types, and Functions
`WriteConfig(config, out)` marshals `Config` using `protojson.MarshalOptions` with multiline indentation, proto field names, enum names, and unpopulated fields. `ReadConfig(in)` reads all JSON and unmarshals with `DiscardUnknown` for forward and legacy compatibility.

## Control Flow
Writing marshals the config, writes the bytes, then writes a trailing newline. Reading consumes the entire reader, allocates a new `Config`, and unmarshals JSON into it.

## State and Persistence
This file does not choose the config path but defines the serialized on-disk format used for `/etc/fscrypt.conf`-style configuration. It does not call `CheckValidity`; callers must validate after reading.

## Dependencies and Integration Points
Depends on `google.golang.org/protobuf/encoding/protojson` and `io`. The config fields feed actions, protector defaults, policy options, filesystem keyring behavior for v1 policies, and cross-user metadata behavior.

## Risks
Unknown fields are discarded, which is useful for compatibility but can hide misspellings or unsupported settings. `EmitUnpopulated` writes explicit false/zero values, so output changes when schema fields are added.

## Test Signals
`config_test.go` verifies exact JSON shape modulo whitespace, read/write round trip via `proto.Equal`, legacy unknown `compatibility` field handling, default false booleans, and policy version normalization after validity checks.
