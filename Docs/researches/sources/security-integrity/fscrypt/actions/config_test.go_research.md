# sources/security-integrity/fscrypt/actions/config_test.go

## Purpose
Tests global config creation behavior that matters for install safety and policy-version selection.

## APIs and Control Flow
`TestConfigFileIsCreatedWithCorrectMode` sets a restrictive umask, redirects `ConfigFileLocation` to a temp file, calls `CreateConfigFile`, and verifies final mode `0644`. `TestCreateConfigFileV2Policy` creates a config with policy version `2`, reloads it through `getConfig`, and checks that `Options.PolicyVersion` is preserved.

## State, Dependencies, and Integration
Tests mutate package global `ConfigFileLocation` and process umask. They use `metadata.Config` via `getConfig`, so they exercise the real serializer and defaulting path rather than inspecting file bytes directly.

## Risks and Test Signals
The umask test protects against accidentally creating a private or overly permissive config due to process umask. Tests do not restore `ConfigFileLocation`, so test ordering relies on later setup resetting it. Hashing is run with a millisecond target to keep tests bounded.
