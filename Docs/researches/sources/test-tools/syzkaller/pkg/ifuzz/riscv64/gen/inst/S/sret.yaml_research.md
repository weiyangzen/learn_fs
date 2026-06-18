# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/S/sret.yaml

## Purpose

`sret.yaml` is a riscv-unified-db YAML descriptor for `sret`, a supervisor memory-management instruction in the `S` source folder. It is declared as `kind: instruction` and `definedBy` resolves to `S`. Its long name is "Supervisor Mode Return from Trap". The descriptor says: Returns from supervisor mode after handling a trap. When `sret` is allowed to execute, its behavior depends on whether or not the current privilege mode is virtualized. *When the current privilege mode is (H)S-mode or M-mode* `sret` sets `hstatus.HPV` = 0, `mstatus.SPP` = 0, `mstatus.SIE` = `mstatus.SPIE`, and `mstatus.SPIE` = 1, changes the privilege mode according to the table below, and then jumps to the address in `sepc`. .Next privilege mode following an `sret` in (H)S-mode or M-mode [%autowidth] |=== | [.rotate]#`mstatus.SPP`# | [.rotate]#`hstatus.SPV`# .>| Mode after `sret` | 0 | 0 | U-mode | 0 | 1 | VU-mode | 1 | 0 | (H)S-mode | 1 | 1 | VS-mode |=== *When the current privilege mode is VS-mode* `sret` sets `vsstatus.SPP` = 0, `vsstatus.SIE` = `vstatus.SPIE`, and `vsstatus.SPIE` = 1, changes the privilege mode according to the table below, and then jumps to the address in `vsepc`. .Next privilege mode following an `sret` in (H)S-mode or M-mode [%autowidth] |=== | [.rotate]#`vsstatus.SPP`# .>| Mode after `sret` | 0 | VU-mode | 1 | VS-mode |=== In functional terms, it coordinates TLB, address-translation, or instruction-fetch invalidation visible to privileged execution.

## Important APIs, Types, and Functions

This file is declarative data consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, not a runtime Go module. The generator unmarshals it into `instYAML`, and only the instruction name, kind, top-level encoding match, top-level variables, and U/VU access flags affect generated code today. The assembly form is an empty assembly operand list. Encoding variants and fields read from the YAML are: default: match length 32, 32 fixed bits, 0 variable bits; fields no variable fields declared

## Control Flow

Generation starts when `go generate` in `pkg/ifuzz/riscv64` runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` visits this YAML, `yaml.Unmarshal` fills the partial `instYAML` shape, `buildInsn` converts each `0`/`1` in a 32-bit match string into opcode-mask bits, and `parseLocations` converts each `hi-lo` range into `riscv64.InsnField` entries. Discontiguous locations such as immediates split on `|` and receive suffixed field names. The current Go generator can consume this descriptor directly: top-level `encoding.match` is 32 bits with 32 fixed bits and 0 operand bits.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent effect is the generated `riscv64.Insn` table entry, where `Name`, `OpcodeMask`, `Opcode`, `Fields`, initial `AsUInt32`, and coarse `Priv` classification are serialized into `generated/insns.go`. At runtime, generated ifuzz templates are copied, operand bits are filled into `AsUInt32`, four little-endian bytes are encoded, and decode checks match by `OpcodeMask`/`Opcode`. The source semantic fields remain in YAML only unless future tooling starts consuming them.

## Dependencies and Integration Points

The descriptor follows the riscv-unified-db instruction schema (`inst_schema.json`) and carries SPDX metadata from the imported source corpus. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `Register`, `ParseInsn`, and the syzkaller `ifuzz/iset` registry. Access metadata is `s=sometimes, u=never, vs=sometimes, vu=never`, and `data_independent_timing` is `None`. The `operation()` block is populated and begins: `# first, check access requirements if (implemented?(ExtensionName::H)) { if (CSR[mstatus].TSR == 1'b0 && CSR[hstatus].VTSR == 1'b0) { if (mode() == PrivilegeMode::U) { raise (Ex...`. A Sail snippet is embedded for architectural traceability and can be compared with the descriptor fields when auditing semantics.

## Risks and Edge Cases

Schema drift is the main maintenance risk: `gen.go` currently reads only `kind`, `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access, while fields such as `description`, `definedBy`, `data_independent_timing`, `operation()`, Sail snippets, `not`, `left_shift`, and nested RV32/RV64 encodings are ignored by generation. For this file, the generator privilege flag would be `True` because access is `s=sometimes, u=never, vs=sometimes, vu=never`. Privilege and architectural side effects are richer than the fuzzer table can express; fuzzing only the raw encoding may miss legality, trap, and state-transition constraints.

## Test Signals

Assert that `sret` is present in or intentionally absent from `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` according to `gen.go`'s top-level-match rule. Compare generated opcode, mask, and `InsnField` ranges against the YAML encoding variant used by the generator. Run RISC-V ifuzz encode/decode round trips so randomized operands preserve fixed bits and `ParseInsn` recognizes the resulting word. Use the embedded Sail block as an oracle for semantic spot checks when available. Cross-check the `operation()` pseudocode against the RISC-V specification for edge cases such as sign extension, divide-by-zero, rounding, masks, and traps.
