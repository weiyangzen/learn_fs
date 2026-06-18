# sources/test-tools/syzkaller/prog/encoding.go

Purpose: implements human-readable program serialization/deserialization, data literal encoding, comment handling, `AUTO` fixups, conditional fixups, and conservative call-set parsing.

Important APIs/types/functions: `Prog.String`, `Serialize`, `SerializeVerbose`, `serializer.call/arg`, concrete `serialize` methods, `DeserializeMode`, `Target.Deserialize`, parser methods `parseProg`, `parseCallProps`, `parseArg*`, `deserializeData`, `fixupAutos`, `fixupConditionals`, `CallSet`, and `highlightError`.

Control flow and state: serialization assigns result variable IDs lazily, omits defaults unless verbose, handles `ANY=`, compressed-image elision, call props, and readable versus hex data. Deserialization scans line by line, attaches comments, parses calls/args/properties, repairs malformed input in non-strict mode, validates with transient conditional fields ignored, patches conditionals/AUTO values, and sanitizes unless unsafe. Parser state includes strict/unsafe flags, variable bindings, pending `AUTO` args, current line, and first error.

Dependencies and integration: central integration point for target descriptions, arg constructors, `analysis.go` allocation state, `expr.go` conditionals, image compression, sanitization, executor serialization tests, and almost all package tests.

Risks: parser repair paths (`eatExcessive`, default args, non-strict errors) are compatibility-sensitive. `AUTO` fixups must coordinate sizes, memory allocation, constants, and checksums. Compressed data validation and unsafe modes affect security/safety boundaries. Serializer default elision must not change semantic union choices.

Test signals: `encoding_test.go` extensively covers data escaping, call-set parsing, strict/non-strict repair, `AUTO`, comments, call props, image skipping, random serialize/deserialize equivalence, and executor-byte equivalence after round trip.
