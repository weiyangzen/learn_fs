# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/I/sd.yaml

## Purpose

`sd.yaml` is a riscv-unified-db YAML descriptor for `sd`, a base integer store instruction in the `I` source folder. It is declared as `kind: instruction` and `definedBy` resolves to `I or Zilsd`. Its long name is "Store doubleword". The descriptor says: For RV64, store 64 bits of data from register `xs2` to an address formed by adding `xs1` to a signed offset.  For RV32, store doubleword from even/odd register pair. In functional terms, it computes an address from `xs1` plus an immediate and writes selected bytes from `xs2` to memory.

## Important APIs, Types, and Functions

This file is declarative data consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, not a runtime Go module. The generator unmarshals it into `instYAML`, and only the instruction name, kind, top-level encoding match, top-level variables, and U/VU access flags affect generated code today. The assembly form is `xs2, imm(xs1)`. Encoding variants and fields read from the YAML are: RV32: match length 32, 10 fixed bits, 22 variable bits; fields `imm` at `31-25|11-7`; `xs2` at `24-20` with excluded values; `xs1` at `19-15` RV64: match length 32, 10 fixed bits, 22 variable bits; fields `imm` at `31-25|11-7` and sign extension; `xs2` at `24-20`; `xs1` at `19-15`

## Control Flow

Generation starts when `go generate` in `pkg/ifuzz/riscv64` runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` visits this YAML, `yaml.Unmarshal` fills the partial `instYAML` shape, `buildInsn` converts each `0`/`1` in a 32-bit match string into opcode-mask bits, and `parseLocations` converts each `hi-lo` range into `riscv64.InsnField` entries. Discontiguous locations such as immediates split on `|` and receive suffixed field names. The descriptor uses variant-specific encodings (`RV32, RV64`) rather than a top-level `encoding.match`; the current `instYAML` struct in `gen.go` does not model those nested variants, so this file is skipped by the present generator unless flattened first.

## State and Persistence Behavior

The YAML file has no mutable runtime state. With the current generator shape, this descriptor has no generated-table effect because its encoding is not exposed as a top-level 32-bit match. It remains persistent source metadata until the generator learns the variant encoding form or the YAML is flattened. At runtime, generated ifuzz templates are copied, operand bits are filled into `AsUInt32`, four little-endian bytes are encoded, and decode checks match by `OpcodeMask`/`Opcode`. The source semantic fields remain in YAML only unless future tooling starts consuming them.

## Dependencies and Integration Points

The descriptor follows the riscv-unified-db instruction schema (`inst_schema.json`) and carries SPDX metadata from the imported source corpus. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `Register`, `ParseInsn`, and the syzkaller `ifuzz/iset` registry. Access metadata is `s=always, u=always, vs=always, vu=always`, and `data_independent_timing` is `None`. The `operation()` block is populated and begins: `Bits<64> data; XReg virtual_address = X[xs1] + $signed(imm); if (xlen() == 32) { if (implemented?(ExtensionName::Zclsd)) { data = {X[xs2 + 1], X[xs2]}; } else { raise(ExceptionC...`. A Sail snippet is embedded for architectural traceability and can be compared with the descriptor fields when auditing semantics.

## Risks and Edge Cases

Schema drift is the main maintenance risk: `gen.go` currently reads only `kind`, `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access, while fields such as `description`, `definedBy`, `data_independent_timing`, `operation()`, Sail snippets, `not`, `left_shift`, and nested RV32/RV64 encodings are ignored by generation. For this file, the generator privilege flag would be `False` because access is `s=always, u=always, vs=always, vu=always`. Because the encoding is not top-level, this descriptor can be valid source metadata but still fail to enter `generated/insns.go`.

## Test Signals

Assert that `sd` is present in or intentionally absent from `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` according to `gen.go`'s top-level-match rule. Compare generated opcode, mask, and `InsnField` ranges against the YAML encoding variant used by the generator. Run RISC-V ifuzz encode/decode round trips so randomized operands preserve fixed bits and `ParseInsn` recognizes the resulting word. Use the embedded Sail block as an oracle for semantic spot checks when available. Cross-check the `operation()` pseudocode against the RISC-V specification for edge cases such as sign extension, divide-by-zero, rounding, masks, and traps.
