# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vand.vx.yaml

## Purpose

`vand.vx.yaml` is a riscv-unified-db YAML descriptor for `vand.vx`, a vector integer bitwise-and instruction in the `V` source folder. It is declared as `kind: instruction` and `definedBy` resolves to `V`. Its long name is "No synopsis available". The descriptor says: No description available. In functional terms, it ANDs vector elements with vector, scalar, or immediate operands under `vm` masking.

## Important APIs, Types, and Functions

This file is declarative data consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, not a runtime Go module. The generator unmarshals it into `instYAML`, and only the instruction name, kind, top-level encoding match, top-level variables, and U/VU access flags affect generated code today. The assembly form is `vd, vs2, xs1, vm`. Encoding variants and fields read from the YAML are: default: match length 32, 16 fixed bits, 16 variable bits; fields `vm` at `25-25`; `vs2` at `24-20`; `xs1` at `19-15`; `vd` at `11-7`

## Control Flow

Generation starts when `go generate` in `pkg/ifuzz/riscv64` runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` visits this YAML, `yaml.Unmarshal` fills the partial `instYAML` shape, `buildInsn` converts each `0`/`1` in a 32-bit match string into opcode-mask bits, and `parseLocations` converts each `hi-lo` range into `riscv64.InsnField` entries. Discontiguous locations such as immediates split on `|` and receive suffixed field names. The current Go generator can consume this descriptor directly: top-level `encoding.match` is 32 bits with 16 fixed bits and 16 operand bits.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent effect is the generated `riscv64.Insn` table entry, where `Name`, `OpcodeMask`, `Opcode`, `Fields`, initial `AsUInt32`, and coarse `Priv` classification are serialized into `generated/insns.go`. At runtime, generated ifuzz templates are copied, operand bits are filled into `AsUInt32`, four little-endian bytes are encoded, and decode checks match by `OpcodeMask`/`Opcode`. The source semantic fields remain in YAML only unless future tooling starts consuming them.

## Dependencies and Integration Points

The descriptor follows the riscv-unified-db instruction schema (`inst_schema.json`) and carries SPDX metadata from the imported source corpus. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `Register`, `ParseInsn`, and the syzkaller `ifuzz/iset` registry. Access metadata is `s=always, u=always, vs=always, vu=always`, and `data_independent_timing` is `False`. The `operation()` block is present but empty, so this file currently relies on encoding metadata, description text, and any Sail block for semantic traceability. A Sail snippet is embedded for architectural traceability and can be compared with the descriptor fields when auditing semantics.

## Risks and Edge Cases

Schema drift is the main maintenance risk: `gen.go` currently reads only `kind`, `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access, while fields such as `description`, `definedBy`, `data_independent_timing`, `operation()`, Sail snippets, `not`, `left_shift`, and nested RV32/RV64 encodings are ignored by generation. For this file, the generator privilege flag would be `False` because access is `s=always, u=always, vs=always, vu=always`. Vector descriptors depend on `vm`, `vstart`, SEW, LMUL, and mask/tail policy; the current generator records bitfields only, not these legality constraints.

## Test Signals

Assert that `vand.vx` is present in or intentionally absent from `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` according to `gen.go`'s top-level-match rule. Compare generated opcode, mask, and `InsnField` ranges against the YAML encoding variant used by the generator. Run RISC-V ifuzz encode/decode round trips so randomized operands preserve fixed bits and `ParseInsn` recognizes the resulting word. Use the embedded Sail block as an oracle for semantic spot checks when available.
