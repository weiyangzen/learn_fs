# sources/sync-backup/kopia/repo/manifest/serialized_test.go

Purpose: tests the custom manifest JSON decoder against complete structs, valid inputs, and malformed inputs.

Important APIs/types/functions: `checkPopulated`, `allPopulated`, `TestManifestDecode_GetsAllFields`, `TestManifestDecode_GoodInput`, and `TestManifestDecode_BadInput`.

Control flow: reflection helpers ensure fixture structs have non-zero fields so decoder tests are meaningful. Good inputs decode and compare expected manifests; bad inputs from testdata assert decoder errors.

State/persistence behavior: no repository state; validates the persisted manifest JSON format parser.

Dependencies/integration: uses `manifest/testdata`, `encoding/json`, reflection, slices, and `testify`.

Risks/test signals: catches field-loss when decoder changes. Bad-input fixtures protect error paths for repeated fields, malformed arrays, token mismatches, and EOF cases.
