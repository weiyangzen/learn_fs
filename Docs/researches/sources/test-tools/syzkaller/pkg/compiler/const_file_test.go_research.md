# sources/test-tools/syzkaller/pkg/compiler/const_file_test.go

Purpose: Unit tests for `.const` file serialization and deserialization.

Important APIs/types/functions: `TestConstFile`.

Control flow: The test builds three architecture constant maps with all-different, all-same, partially undefined, and fully undefined constants. It serializes them, compares exact text, checks `ExistsAny`, deserializes the new format from a temp file, and deserializes old per-arch files from a temp dir.

State and persistence behavior: Writes temporary const files only. Expected serialized string is embedded in the test.

Dependencies/integration points: Tests `NewConstFile`, `AddArch`, `Serialize`, `DeserializeConstFile`, `Arch`, and `ExistsAny`.

Risks: Exact output formatting is part of the contract; changes to compaction/order require updating the expected string.

Test signals: Strong coverage for const file compatibility and undefined/default encoding.
