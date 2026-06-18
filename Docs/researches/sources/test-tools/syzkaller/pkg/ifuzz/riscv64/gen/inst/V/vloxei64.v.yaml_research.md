# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vloxei64.v.yaml

## Purpose

`vloxei64.v.yaml` describes `vloxei64.v`, a ordered indexed vector load using 64-bit indices, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. The file is a riscv-unified-db instruction YAML record: it supplies the mnemonic, assembly operands `vd, (xs1), vs2, vm`, privilege/access metadata, and the 32-bit encoding pattern used to create a generated decode/fuzzing table entry.

## Important APIs, Types, and Functions

The local schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vloxei64.v`, `assembly=vd, (xs1), vs2, vm`, `encoding.match=000011-----------111-----0000111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7]`, `access=[s=always, u=always, vs=always, vu=always]`, and `data_independent_timing=False`. In `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, these map to the `instYAML` struct, `buildInsn`, `parseLocations`, and `parseRange`; successful parsing creates a `riscv64.Insn` with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv` populated. For this file the computed opcode is `0x0c007007` and opcode mask is `0xfc00707f`.
The embedded `sail()` block is reference semantics for architecture readers and validation work. Notable helper calls in this file include `get_lmul_pow`, `get_num_elem`, `get_sew_bytes`, `get_sew_pow`, `handle_illegal`, `illegal_indexed_load`, `nfields_int`, `operation`, `process_vlxseg`, `sail`, `vlewidth_bytesnumber`, `vlewidth_pow`, but the current Go generator does not parse or execute that block.

## Control Flow

During generation, `gen.go` walks the instruction tree, unmarshals this YAML with `gopkg.in/yaml.v3`, requires `kind: instruction`, requires a 32-character match string, converts fixed `0`/`1` bits into opcode and mask values, expands each variable location into an `InsnField`, marks the instruction privileged only when user access is denied, and serializes the resulting instruction table. The reference operation models a ordered indexed vector load using 64-bit indices. It computes EEW, EMUL, element count, mask behavior, and load legality, then calls the Sail helper (`process_vlseg`, `process_vlxseg`, or the corresponding strided/indexed variant) to perform memory reads and destination register updates.

## State and Persistence Behavior

The YAML file itself has no runtime state. Its persistent effect is through generated Go output, normally `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vloxei64.v` becomes an immutable instruction-table element registered at package init. The architectural state named in the Sail text, when present, is vector register state, mask state, floating-point flags/rounding state, `vstart`, and memory for load forms; none of that state is persisted by this YAML or by the decode generator.

## Dependencies and Integration Points

This file depends on the riscv-unified-db instruction schema and on the vector extension namespace. Its direct integration point in this repository is `pkg/ifuzz/riscv64/gen/gen.go`, which in turn depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, the generated instruction table is registered by `pkg/ifuzz/riscv64/generated` and used by syzkaller instruction fuzzing to enumerate and instantiate RISC-V encodings. The assembly operands `vd, (xs1), vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `xs1` bits 19-15, `vd` bits 11-7] for generated operands to be meaningful.

## Risks and Edge Cases

load forms are sensitive to EEW/EMUL, mask, register-group overlap, and fault-only-first or indexed ordering behavior that the current generator does not validate the generator ignores description, long_name, data_independent_timing, most access modes, and Sail code, so YAML schema drift can silently reduce semantic coverage while still producing an instruction entry

## Test Signals

run the RISC-V ifuzz generator over this YAML tree and confirm the generated `Insn` keeps this mnemonic, opcode, mask, and decoded fields; compare against Sail/spec execution for representative legal and illegal vector configurations; exercise masked and unmasked loads, boundary addresses, segment field counts, and EEW/LMUL combinations.
