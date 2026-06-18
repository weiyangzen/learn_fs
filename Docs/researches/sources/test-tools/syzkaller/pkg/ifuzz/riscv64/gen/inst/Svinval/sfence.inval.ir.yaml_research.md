# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Svinval/sfence.inval.ir.yaml

## Purpose

`sfence.inval.ir.yaml` is a riscv-unified-db YAML descriptor for `sfence.inval.ir`, a supervisor memory-management instruction in the `Svinval` source folder. It is declared as `kind: instruction` and `definedBy` resolves to `Svinval`. Its long name is "Order implicit page table reads after invalidation". The descriptor says: The `sfence.inval.ir` instruction guarantees that any previous `sinval.vma` instructions executed by the current hart are ordered before subsequent implicit references by that hart to the memory-management data structures. In functional terms, it coordinates TLB, address-translation, or instruction-fetch invalidation visible to privileged execution.

## Important APIs, Types, and Functions

This file is declarative data consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, not a runtime Go module. The generator unmarshals it into `instYAML`, and only the instruction name, kind, top-level encoding match, top-level variables, and U/VU access flags affect generated code today. The assembly form is an empty assembly operand list. Encoding variants and fields read from the YAML are: default: match length 32, 32 fixed bits, 0 variable bits; fields no variable fields declared

## Control Flow

Generation starts when `go generate` in `pkg/ifuzz/riscv64` runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` visits this YAML, `yaml.Unmarshal` fills the partial `instYAML` shape, `buildInsn` converts each `0`/`1` in a 32-bit match string into opcode-mask bits, and `parseLocations` converts each `hi-lo` range into `riscv64.InsnField` entries. Discontiguous locations such as immediates split on `|` and receive suffixed field names. The current Go generator can consume this descriptor directly: top-level `encoding.match` is 32 bits with 32 fixed bits and 0 operand bits.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent effect is the generated `riscv64.Insn` table entry, where `Name`, `OpcodeMask`, `Opcode`, `Fields`, initial `AsUInt32`, and coarse `Priv` classification are serialized into `generated/insns.go`. At runtime, generated ifuzz templates are copied, operand bits are filled into `AsUInt32`, four little-endian bytes are encoded, and decode checks match by `OpcodeMask`/`Opcode`. The source semantic fields remain in YAML only unless future tooling starts consuming them.

## Dependencies and Integration Points

The descriptor follows the riscv-unified-db instruction schema (`inst_schema.json`) and carries SPDX metadata from the imported source corpus. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `Register`, `ParseInsn`, and the syzkaller `ifuzz/iset` registry. Access metadata is `s=sometimes, u=never, vs=sometimes, vu=never`, and `data_independent_timing` is `None`. The `operation()` block is populated and begins: `if (mode() == PrivilegeMode::U) { raise (ExceptionCode::IllegalInstruction, mode(), $encoding); } if (CSR[misa].H == 1 && mode() == PrivilegeMode::VU) { raise (ExceptionCode::Vi...`. No Sail snippet is embedded, so semantic validation must rely on the operation block, the RISC-V spec, or adjacent descriptors.

## Risks and Edge Cases

Schema drift is the main maintenance risk: `gen.go` currently reads only `kind`, `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access, while fields such as `description`, `definedBy`, `data_independent_timing`, `operation()`, Sail snippets, `not`, `left_shift`, and nested RV32/RV64 encodings are ignored by generation. For this file, the generator privilege flag would be `True` because access is `s=sometimes, u=never, vs=sometimes, vu=never`. Privilege and architectural side effects are richer than the fuzzer table can express; fuzzing only the raw encoding may miss legality, trap, and state-transition constraints.

## Test Signals

Assert that `sfence.inval.ir` is present in or intentionally absent from `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` according to `gen.go`'s top-level-match rule. Compare generated opcode, mask, and `InsnField` ranges against the YAML encoding variant used by the generator. Run RISC-V ifuzz encode/decode round trips so randomized operands preserve fixed bits and `ParseInsn` recognizes the resulting word. Cross-check the `operation()` pseudocode against the RISC-V specification for edge cases such as sign extension, divide-by-zero, rounding, masks, and traps.
