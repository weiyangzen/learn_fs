# sources/test-tools/syzkaller/prog/encoding_test.go

Purpose: validates text serialization/deserialization, repair behavior, data encoding, comments, call props, image skipping, and text-to-executor semantic stability.

Important APIs/types/functions: `TestSerializeData`, `TestCallSet`, `TestCallSetRandom`, `TestDeserialize`, `TestSerializeDeserialize`, `TestDeserializeDataMmapProg`, `TestSerializeDeserializeRandom`, `testSerializeDeserialize`, `TestSerializeCallProps`, `TestDeserializeComments`, `TestHasNext`, and `TestDeserializeSkipImage`.

Control flow and state: table-driven tests feed malformed and valid programs through strict/non-strict modes and compare expected serialized output or expected errors. Random tests generate programs, serialize to text, deserialize, and require identical executor buffers. Failure minimization uses `Minimize` to shrink random counterexamples.

Dependencies and integration: uses target test helpers, `DeserializeTest` helpers from surrounding package tests, `SerializeForExec`, `DeserializeExec`, `Minimize`, `pkg/image`, and `testify`.

Risks: exact strings couple tests to serializer formatting. Random round-trip checks can be expensive and skip very large arg trees. The suite encodes many compatibility contracts; changing text syntax requires broad updates.

Test signals: very strong coverage for parser recovery, `AUTO`, special pointers, strings/globs, out args, vma clamping, call props, comments, compressed image elision, and executor-equivalence preservation.
