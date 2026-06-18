# sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/string_operations.go

Purpose: small string and naming helpers for integration tests.

Important APIs/types/functions: `VerifyExpectedSubstrings`, `VerifyUnexpectedSubstrings`, `GetRandomName`, and `SplitBucketNameAndDirPath`.

Control flow: substring helpers iterate expected or unexpected fragments and record `t.Errorf`; random names use `uuid.NewRandom`; bucket splitting requires the form `<bucket>/<object-name>` and fails tests if no slash is present.

State/persistence behavior: no persistent state. The only state produced is a random UUID string.

Dependencies/integration: used by tests that verify command output, logs, or bucket/object path parsing.

Risks/test signals: substring checks continue after failures because they use `Errorf`, while split parsing uses `Fatalf`. `SplitBucketNameAndDirPath` only splits once, preserving deeper object paths.
