# sources/test-tools/syzkaller/pkg/compiler/const_file.go

Purpose: Serializer/deserializer for syzkaller `.const` files containing per-architecture constant values and undefined constants.

Important APIs/types/functions: `ConstFile`, `constVal`, `undefined`, `NewConstFile`, `AddArch`, `addConst`, `Arch`, `ExistsAny`, `Serialize`, `DeserializeConstFile`, `deserializeFile`, `parseConst`, and `parseOldConst`.

Control flow: `AddArch` records declared constants and undefined names for an arch. `Serialize` sorts arches/constants, chooses a default value when repeated across arches, and emits compact arch-specific overrides or `???`. `DeserializeConstFile` expands a glob, supports old per-arch filename format, detects weak `auto.txt.const`, and parses new compact lines.

State and persistence behavior: In-memory maps track arches and constant values/weak flags. Serialized text is persistent state used by sysgen and compiler tests. Weak values can be replaced on mismatch rather than erroring.

Dependencies/integration points: Used by compiler tests and sys description compilation to load constants. Error reporting uses `ast.ErrorHandler`.

Risks: `parseConst` assumes an `arches =` header for new format. Duplicate/mismatched non-weak values fail. Old-format support depends on `_([a-z0-9]+).const` filename matching and is marked temporary.

Test signals: `const_file_test.go` validates serialization, deserialization, undefined handling, defaults, per-arch values, and old-format compatibility.
