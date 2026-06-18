# sources/test-tools/syzkaller/pkg/ifuzz/arm64/gen/gen.go

## Purpose
`gen.go` is the ARM64 instruction-table generator. It converts JSON instruction descriptions into Go source that registers `arm64.Insn` templates.

## Important APIs, Types, And Functions
`main` is the generator entry point used by `go:generate` in `arm64.go`. `insnDesc` mirrors the relevant JSON fields: `Name`, `Bits`, `Arch`, `Syntax`, `Code`, and `Alias`. `isPrivateInsn` marks privileged/system instructions. `JSONToInsns(jsonStr)` parses JSON descriptions into `[]*arm64.Insn`.

## Control Flow
`main` requires exactly input JSON and output file arguments, reads the JSON, calls `JSONToInsns`, writes a generated Go file header and package body that imports ARM64 types, emits an init function calling `Register(insns_arm64)`, serializes the instruction slice with `serializer.Write`, atomically writes the output file, and prints the handled count to stderr. `JSONToInsns` unmarshals descriptions, then for each `Bits` string splits fields by `|`, parses optional `pattern:size` suffixes, walks from bit 31 downward, and builds opcode and mask values. Binary patterns contribute fixed opcode and mask bits. Non-binary named regions become `InsnField` entries. Patterns starting with `(` are treated as opcode-updating zero bits. Each template is marked privileged when its name is in the system instruction switch.

## State And Persistence Behavior
The generator reads one JSON file and atomically writes one Go file. It does not persist intermediate state. The generated file becomes compile-time registration state for the ARM64 backend.

## Dependencies And Integration Points
It depends on `pkg/ifuzz/arm64`, `pkg/osutil` atomic file writing, `pkg/serializer` for Go literal emission, and `pkg/tool` for fatal errors. It is invoked by the `//go:generate` directive in `arm64.go` with `gen/json/arm64.json` and `generated/insns.go`.

## Risks And Edge Cases
`JSONToInsns` returns nil on unmarshal or parse errors instead of surfacing diagnostics, so `main` may generate an empty table without a clear parse failure except the handled count. The `pattern[0:1]` indexing assumes non-empty bit pieces. `curBit -= size` can underflow if the bit description exceeds 32 bits. Parenthesized patterns are not parsed as numeric masks and effectively update opcode/mask as zero-width fixed bits after shifting, so the JSON contract must match this behavior. Privileged classification is name-based and must be updated as instruction coverage grows.

## Test Signals
Generator tests should feed small JSON fixtures with fixed bits, named fields, sized regions, aliases, and invalid input. Downstream compile and ARM64 decode tests catch many generated-table regressions, but direct tests would make parse failures easier to diagnose.
