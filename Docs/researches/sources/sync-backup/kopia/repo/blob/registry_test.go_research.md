# sources/sync-backup/kopia/repo/blob/registry_test.go

Purpose: tests blob storage registration and connection info JSON behavior.

Important APIs/types/functions: `myConfig`, `myStorage`, `TestRegistry`, and `TestConnectionInfo`.

Control flow: tests register a fake storage type, create storage through `NewStorage`, and verify unknown types/error paths. Connection info tests marshal/unmarshal typed config and ensure the default config/factory registry participates correctly.

State and persistence behavior: tests mutate the global `factories` map by adding a test provider. JSON strings act as persistent config samples.

Dependencies/integration points: validates `registry.go` and `config.go` together. Risks/test gaps include global registry pollution across tests, no duplicate-registration behavior check, and no concurrent registration/use coverage. The tests protect the basic config-to-factory path used by every real provider.
