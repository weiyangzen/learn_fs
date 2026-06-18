# sources/security-integrity/fscrypt/metadata/config_test.go

## Purpose
This file tests JSON config serialization, deserialization, and compatibility with older config files.

## Important APIs, Types, and Functions
`testConfig` and `testConfigString` define the expected config object and JSON. `compact` normalizes JSON for comparison. Tests are `TestWrite`, `TestRead`, and `TestOptionalFields`.

## Control Flow
`TestWrite` serializes the config and compares compacted JSON. `TestRead` parses the fixture and compares protobuf equality. `TestOptionalFields` parses a legacy JSON document without newer fields and with the removed `compatibility` field, then validates defaults and `CheckValidity` normalization.

## State and Persistence
All config data is in memory. No real config files are written.

## Dependencies and Integration Points
Uses `encoding/json` for test normalization and protobuf equality. It validates behavior consumed by actions and PAM configuration loading.

## Risks
Exact JSON expectations can need updates when proto schema or marshal options change. The test checks compatibility but not invalid configs or malformed JSON.

## Test Signals
The tests confirm proto field names, enum names, int64 string encoding in protojson, emitted false booleans, unknown-field discard, and legacy policy-version upgrade from `0` to `1`.
