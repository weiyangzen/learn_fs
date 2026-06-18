# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vl2re64.v.yaml

## Purpose

`vl2re64.v.yaml` describes `vl2re64.v`, a whole-register load of 2 vector register group(s) with element width 64, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. The file is a riscv-unified-db instruction YAML record: it supplies the mnemonic, assembly operands `vd, (xs1)`, privilege/access metadata, and the 32-bit encoding pattern used to create a generated decode/fuzzing table entry.

## Important APIs, Types, and Functions

The local schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vl2re64.v`, `assembly=vd, (xs1)`, `encoding.match=001000101000-----111-----0000111`, `encoding.variables=[`xs1` bits 19-15, `vd` bits 11-7]`, `access=[s=always, u=always, vs=always, vu=always]`, and `data_independent_timing=False`. In `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, these map to the `instYAML` struct, `buildInsn`, `parseLocations`, and `parseRange`; successful parsing creates a `riscv64.Insn` with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv` populated. For this file the computed opcode is `0x22807007` and opcode mask is `0xfff0707f`.
The `operation()` literal is empty in this YAML, so there are no local semantic helper calls to inspect; generation still succeeds because the Go generator only depends on decode metadata.

## Control Flow

During generation, `gen.go` walks the instruction tree, unmarshals this YAML with `gopkg.in/yaml.v3`, requires `kind: instruction`, requires a 32-character match string, converts fixed `0`/`1` bits into opcode and mask values, expands each variable location into an `InsnField`, marks the instruction privileged only when user access is denied, and serializes the resulting instruction table. This is a whole-register load of 2 vector register group(s) with element width 64. The YAML is primarily an encoding record; in this source snapshot its `operation()` block is empty, so the ifuzz generator only receives decode metadata, while architectural load semantics must come from the RISC-V vector spec or surrounding unified-db data.

## State and Persistence Behavior

The YAML file itself has no runtime state. Its persistent effect is through generated Go output, normally `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vl2re64.v` becomes an immutable instruction-table element registered at package init. The architectural state named in the Sail text, when present, is vector register state, mask state, floating-point flags/rounding state, `vstart`, and memory for load forms; none of that state is persisted by this YAML or by the decode generator.

## Dependencies and Integration Points

This file depends on the riscv-unified-db instruction schema and on the vector extension namespace. Its direct integration point in this repository is `pkg/ifuzz/riscv64/gen/gen.go`, which in turn depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, the generated instruction table is registered by `pkg/ifuzz/riscv64/generated` and used by syzkaller instruction fuzzing to enumerate and instantiate RISC-V encodings. The assembly operands `vd, (xs1)` must remain consistent with the variable fields [`xs1` bits 19-15, `vd` bits 11-7] for generated operands to be meaningful.

## Risks and Edge Cases

the empty operation block means this file contributes decode metadata but no embedded reference semantics load forms are sensitive to EEW/EMUL, mask, register-group overlap, and fault-only-first or indexed ordering behavior that the current generator does not validate the generator ignores description, long_name, data_independent_timing, most access modes, and Sail code, so YAML schema drift can silently reduce semantic coverage while still producing an instruction entry

## Test Signals

run the RISC-V ifuzz generator over this YAML tree and confirm the generated `Insn` keeps this mnemonic, opcode, mask, and decoded fields; add a decode-only regression because no local Sail operation is present; exercise masked and unmasked loads, boundary addresses, segment field counts, and EEW/LMUL combinations.
