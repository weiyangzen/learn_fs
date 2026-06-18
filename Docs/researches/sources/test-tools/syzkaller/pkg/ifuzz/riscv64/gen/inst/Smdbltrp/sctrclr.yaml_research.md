# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Smdbltrp/sctrclr.yaml

## Purpose

`sctrclr.yaml` is a riscv-unified-db YAML descriptor for `sctrclr`, a privileged return/control instruction in the `Smdbltrp` source folder. It is declared as `kind: instruction` and `definedBy` resolves to `Smctr or Ssctr`. Its long name is "Supervisor Control Transfer Record (CTR) clear". The descriptor says: When `mstateen0.CTR`=1, the SCTRCLR instruction performs the following operations: * Zeroes all CTR Entry Registers, for all DEPTH values * Reset to Zero the optional CTR cycle counter where implemented ** `ctrdata.CC` and `ctrdata.CCV` bit fields. Any read of `ctrsource`, `ctrtarget`, or `ctrdata` that follows SCTRCLR, such that it precedes the next qualified control transfer, will return the value 0. Further, the first recorded transfer following SCTRCLR will have `ctrdata.CCV`=0. SCTRCLR execution causes an `IllegalInstruction` exception if: * `Smctr` is not implemented * The instruction is executed in S/VS/VU-mode and `Ssctr` is not implemented, or `mstateen0.CTR`=0 * The instruction is executed in U-mode SCTRCLR execution causes a `VirtualInstruciton` exception if `mstateen0.CTR`=1 and: * The instruction is executed in VS-mode and `hstateen0.CTR`=0 * The instruction is executed in VU-mode In functional terms, it transitions privileged architectural state according to its extension-specific return or trap-control semantics.

## Important APIs, Types, and Functions

This file is declarative data consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, not a runtime Go module. The generator unmarshals it into `instYAML`, and only the instruction name, kind, top-level encoding match, top-level variables, and U/VU access flags affect generated code today. The assembly form is an empty assembly operand list. Encoding variants and fields read from the YAML are: default: match length 32, 32 fixed bits, 0 variable bits; fields no variable fields declared

## Control Flow

Generation starts when `go generate` in `pkg/ifuzz/riscv64` runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` visits this YAML, `yaml.Unmarshal` fills the partial `instYAML` shape, `buildInsn` converts each `0`/`1` in a 32-bit match string into opcode-mask bits, and `parseLocations` converts each `hi-lo` range into `riscv64.InsnField` entries. Discontiguous locations such as immediates split on `|` and receive suffixed field names. The current Go generator can consume this descriptor directly: top-level `encoding.match` is 32 bits with 32 fixed bits and 0 operand bits.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent effect is the generated `riscv64.Insn` table entry, where `Name`, `OpcodeMask`, `Opcode`, `Fields`, initial `AsUInt32`, and coarse `Priv` classification are serialized into `generated/insns.go`. At runtime, generated ifuzz templates are copied, operand bits are filled into `AsUInt32`, four little-endian bytes are encoded, and decode checks match by `OpcodeMask`/`Opcode`. The source semantic fields remain in YAML only unless future tooling starts consuming them.

## Dependencies and Integration Points

The descriptor follows the riscv-unified-db instruction schema (`inst_schema.json`) and carries SPDX metadata from the imported source corpus. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `Register`, `ParseInsn`, and the syzkaller `ifuzz/iset` registry. Access metadata is `s=always, u=always, vs=always, vu=always`, and `data_independent_timing` is `False`. The `operation()` block is present but empty, so this file currently relies on encoding metadata, description text, and any Sail block for semantic traceability. No Sail snippet is embedded, so semantic validation must rely on the operation block, the RISC-V spec, or adjacent descriptors.

## Risks and Edge Cases

Schema drift is the main maintenance risk: `gen.go` currently reads only `kind`, `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access, while fields such as `description`, `definedBy`, `data_independent_timing`, `operation()`, Sail snippets, `not`, `left_shift`, and nested RV32/RV64 encodings are ignored by generation. For this file, the generator privilege flag would be `False` because access is `s=always, u=always, vs=always, vu=always`. Privilege and architectural side effects are richer than the fuzzer table can express; fuzzing only the raw encoding may miss legality, trap, and state-transition constraints.

## Test Signals

Assert that `sctrclr` is present in or intentionally absent from `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` according to `gen.go`'s top-level-match rule. Compare generated opcode, mask, and `InsnField` ranges against the YAML encoding variant used by the generator. Run RISC-V ifuzz encode/decode round trips so randomized operands preserve fixed bits and `ParseInsn` recognizes the resulting word.
