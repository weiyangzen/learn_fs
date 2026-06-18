# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/I/wfi.yaml

## Purpose

`wfi.yaml` is a riscv-unified-db YAML descriptor for `wfi`, a base privileged/system wait instruction in the `I` source folder. It is declared as `kind: instruction` and `definedBy` resolves to `Sm`. Its long name is "Wait for interrupt". The descriptor says: Can causes the processor to enter a low-power state until the next interrupt occurs.  The behavior of `wfi` is affected by the `mstatus.TW` and `hstatus.VTW` bits, as summarized below. [%autowidth,%footer] |=== .2+| [.rotate]#`mstatus.TW`# .2+| [.rotate]#`hstatus.VTW`# 4+^.>| `wfi` behavior h| HS-mode h| U-mode h| VS-mode h| in VU-mode | 0 | 0 | Wait | Trap (I) | Wait | Trap (V) | 0 | 1 | Wait | Trap (I) | Trap (V) | Trap (V) | 1 | - | Trap (I) | Trap (I) | Trap (I) | Trap (I) 6+| Trap (I) - Trap with `Illegal Instruction` code + Trap (V) - Trap with `Virtual Instruction` code |===  The `wfi` instruction is also affected by `mstatus.TW`, as shown below: [%autowidth,%footer] |=== .2+| [.rotate]#`mstatus.TW`# 2+^.>| `wfi` behavior h| S-mode h| U-mode | 0 | Wait | Trap (I) | 1 | Trap (I) | Trap (I) 3+| Trap (I) - Trap with `Illegal Instruction` code |===  When `wfi` is marked as causing a trap above, the implementation is allowed to wait for an unspecified period of time to see if an interrupt occurs before raising the trap. That period of time can be zero (_i.e._, `wfi` always causes a trap in the cases identified above). In functional terms, it requests a low-power wait-for-interrupt behavior whose legality depends on privilege and status bits.

## Important APIs, Types, and Functions

This file is declarative data consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, not a runtime Go module. The generator unmarshals it into `instYAML`, and only the instruction name, kind, top-level encoding match, top-level variables, and U/VU access flags affect generated code today. The assembly form is an empty assembly operand list. Encoding variants and fields read from the YAML are: default: match length 32, 32 fixed bits, 0 variable bits; fields no variable fields declared

## Control Flow

Generation starts when `go generate` in `pkg/ifuzz/riscv64` runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` visits this YAML, `yaml.Unmarshal` fills the partial `instYAML` shape, `buildInsn` converts each `0`/`1` in a 32-bit match string into opcode-mask bits, and `parseLocations` converts each `hi-lo` range into `riscv64.InsnField` entries. Discontiguous locations such as immediates split on `|` and receive suffixed field names. The current Go generator can consume this descriptor directly: top-level `encoding.match` is 32 bits with 32 fixed bits and 0 operand bits.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent effect is the generated `riscv64.Insn` table entry, where `Name`, `OpcodeMask`, `Opcode`, `Fields`, initial `AsUInt32`, and coarse `Priv` classification are serialized into `generated/insns.go`. At runtime, generated ifuzz templates are copied, operand bits are filled into `AsUInt32`, four little-endian bytes are encoded, and decode checks match by `OpcodeMask`/`Opcode`. The source semantic fields remain in YAML only unless future tooling starts consuming them.

## Dependencies and Integration Points

The descriptor follows the riscv-unified-db instruction schema (`inst_schema.json`) and carries SPDX metadata from the imported source corpus. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `Register`, `ParseInsn`, and the syzkaller `ifuzz/iset` registry. Access metadata is `s=sometimes, u=sometimes, vs=sometimes, vu=sometimes`, and `data_independent_timing` is `None`. The `operation()` block is populated and begins: `# first, perform all the access checks if (mode() == PrivilegeMode::U) { raise (ExceptionCode::IllegalInstruction, mode(), $encoding); } if ((CSR[misa].S == 1) && (CSR[mstatus]....`. A Sail snippet is embedded for architectural traceability and can be compared with the descriptor fields when auditing semantics.

## Risks and Edge Cases

Schema drift is the main maintenance risk: `gen.go` currently reads only `kind`, `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access, while fields such as `description`, `definedBy`, `data_independent_timing`, `operation()`, Sail snippets, `not`, `left_shift`, and nested RV32/RV64 encodings are ignored by generation. For this file, the generator privilege flag would be `False` because access is `s=sometimes, u=sometimes, vs=sometimes, vu=sometimes`. Privilege and architectural side effects are richer than the fuzzer table can express; fuzzing only the raw encoding may miss legality, trap, and state-transition constraints.

## Test Signals

Assert that `wfi` is present in or intentionally absent from `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` according to `gen.go`'s top-level-match rule. Compare generated opcode, mask, and `InsnField` ranges against the YAML encoding variant used by the generator. Run RISC-V ifuzz encode/decode round trips so randomized operands preserve fixed bits and `ParseInsn` recognizes the resulting word. Use the embedded Sail block as an oracle for semantic spot checks when available. Cross-check the `operation()` pseudocode against the RISC-V specification for edge cases such as sign extension, divide-by-zero, rounding, masks, and traps.
