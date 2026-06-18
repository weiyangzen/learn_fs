# sources/sync-backup/kopia/repo/manifest/testdata/manifests.go

Purpose: provides serialized manifest JSON fixtures for decoder tests.

Important APIs/types/functions: `testInput`, `BadInputs`, good input fixture variables, and expected manifest fixture constants.

Control flow: no executable logic beyond variable initialization. The fixtures include realistic snapshot-like manifest data and malformed cases such as repeated fields or invalid JSON structure.

State/persistence behavior: models persisted manifest JSON payloads used by `serialized_test.go`; no runtime persistence.

Dependencies/integration: imported only by manifest tests.

Risks/test signals: fixture realism helps protect decoder compatibility with historical manifest data. If fixture structs lack populated fields, tests could miss decoder omissions; `allPopulated` in tests mitigates that.
