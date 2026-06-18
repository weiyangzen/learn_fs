# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Q/fclass.q.yaml

## Purpose

`fclass.q.yaml` is a riscv-unified-db YAML descriptor for `fclass.q`, a quad-precision floating-point classification instruction in the `Q` source folder. It is declared as `kind: instruction` and `definedBy` resolves to `Q`. Its long name is "Floating-Point Classify Quad-Precision". The descriptor says: The `fclass.q` instruction examines the value in floating-point register `rs1` and writes to integer register `rd` a 10-bit mask that indicates the class of the floating-point number. The format of the mask is described in table given below. The corresponding bit in `rd` will be set if the property is true and clear otherwise. All other bits in `rd` are cleared. Note that exactly one bit in `rd` will be set. `fclass.q` does not set the floating-point exception flags. .Format of result of `fclass` instruction. [%autowidth,float="center",align="center",cols="^,<",options="header",] |=== |_xd_ bit |Meaning |0 |_fs1_ is latexmath:[$-\infty$]. |1 |_fs1_ is a negative normal number. |2 |_fs1_ is a negative subnormal number. |3 |_fs1_ is latexmath:[$-0$]. |4 |_fs1_ is latexmath:[$+0$]. |5 |_fs1_ is a positive subnormal number. |6 |_fs1_ is a positive normal number. |7 |_fs1_ is latexmath:[$+\infty$]. |8 |_fs1_ is a signaling NaN. |9 |_fs1_ is a quiet NaN. |=== In functional terms, it classifies the FP source into the architectural bit-mask result.

## Important APIs, Types, and Functions

This file is declarative data consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, not a runtime Go module. The generator unmarshals it into `instYAML`, and only the instruction name, kind, top-level encoding match, top-level variables, and U/VU access flags affect generated code today. The assembly form is `xd, fs1`. Encoding variants and fields read from the YAML are: default: match length 32, 22 fixed bits, 10 variable bits; fields `fs1` at `19-15`; `xd` at `11-7`

## Control Flow

Generation starts when `go generate` in `pkg/ifuzz/riscv64` runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` visits this YAML, `yaml.Unmarshal` fills the partial `instYAML` shape, `buildInsn` converts each `0`/`1` in a 32-bit match string into opcode-mask bits, and `parseLocations` converts each `hi-lo` range into `riscv64.InsnField` entries. Discontiguous locations such as immediates split on `|` and receive suffixed field names. The current Go generator can consume this descriptor directly: top-level `encoding.match` is 32 bits with 22 fixed bits and 10 operand bits.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent effect is the generated `riscv64.Insn` table entry, where `Name`, `OpcodeMask`, `Opcode`, `Fields`, initial `AsUInt32`, and coarse `Priv` classification are serialized into `generated/insns.go`. At runtime, generated ifuzz templates are copied, operand bits are filled into `AsUInt32`, four little-endian bytes are encoded, and decode checks match by `OpcodeMask`/`Opcode`. The source semantic fields remain in YAML only unless future tooling starts consuming them.

## Dependencies and Integration Points

The descriptor follows the riscv-unified-db instruction schema (`inst_schema.json`) and carries SPDX metadata from the imported source corpus. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `Register`, `ParseInsn`, and the syzkaller `ifuzz/iset` registry. Access metadata is `s=always, u=always, vs=always, vu=always`, and `data_independent_timing` is `False`. The `operation()` block is present but empty, so this file currently relies on encoding metadata, description text, and any Sail block for semantic traceability. This Q-extension descriptor is encoding-complete for ifuzz but semantically sparse: both executable pseudocode and Sail text are absent.

## Risks and Edge Cases

Schema drift is the main maintenance risk: `gen.go` currently reads only `kind`, `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access, while fields such as `description`, `definedBy`, `data_independent_timing`, `operation()`, Sail snippets, `not`, `left_shift`, and nested RV32/RV64 encodings are ignored by generation. For this file, the generator privilege flag would be `False` because access is `s=always, u=always, vs=always, vu=always`. The absence of pseudocode/Sail in many Q descriptors makes encoding regression tests more important than semantic snippet checks.

## Test Signals

Assert that `fclass.q` is present in or intentionally absent from `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` according to `gen.go`'s top-level-match rule. Compare generated opcode, mask, and `InsnField` ranges against the YAML encoding variant used by the generator. Run RISC-V ifuzz encode/decode round trips so randomized operands preserve fixed bits and `ParseInsn` recognizes the resulting word.
