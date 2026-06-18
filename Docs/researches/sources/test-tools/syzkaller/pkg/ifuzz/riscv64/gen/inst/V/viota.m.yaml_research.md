# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/viota.m.yaml

## Purpose

`viota.m.yaml` describes `viota.m`, a mask population-prefix generation, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative data rather than Go code: the important payload is the mnemonic, assembly operands `vd, vs2, vm`, access metadata, encoding mask, variable fields, and any embedded Sail reference operation.

## Important APIs, Types, and Functions

The local schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=viota.m`, `assembly=vd, vs2, vm`, `encoding.match=010100------10000010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7]`, `access=[s=always, u=always, vs=always, vu=always]`, and `data_independent_timing=False`. In `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, these map to the `instYAML` struct, `buildInsn`, `parseLocations`, and `parseRange`; successful parsing creates a `riscv64.Insn` with `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv` populated. For this file the computed opcode is `0x50082057` and opcode mask is `0xfc0ff07f`.
The embedded `sail()` block is reference semantics for architecture readers and validation work. Notable helper calls in this file include `assert_vstart`, `bits`, `get_lmul_pow`, `get_num_elem`, `get_sew`, `handle_illegal`, `illegal_normal`, `init_masked_result`, `not`, `operation`, `read_vmask`, `read_vreg`, `sail`, `to_bits`, but the current Go generator does not parse or execute that block.

## Control Flow

During generation, `gen.go` walks the instruction tree, unmarshals this YAML with `gopkg.in/yaml.v3`, requires `kind: instruction`, requires a 32-character match string, converts fixed `0`/`1` bits into opcode and mask values, expands each variable location into an `InsnField`, marks the instruction privileged only when user access is denied, and serializes the resulting instruction table. The Sail body computes an inclusive mask-prefix population count into vector elements. It rejects nonzero `vstart` and `vd == vs2`, reads `vs2` as a mask source, counts prior active true mask bits under `vm`, writes the running count to active destination lanes, and clears `vstart`.

## State and Persistence Behavior

The YAML file itself has no runtime state. Its persistent effect is through generated Go output, normally `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `viota.m` becomes an immutable instruction-table element registered at package init. The architectural state named in the Sail text, when present, is vector register state, mask state, floating-point flags/rounding state, `vstart`, and memory for load forms; none of that state is persisted by this YAML or by the decode generator.

## Dependencies and Integration Points

This file depends on the riscv-unified-db instruction schema and on the vector extension namespace. Its direct integration point in this repository is `pkg/ifuzz/riscv64/gen/gen.go`, which in turn depends on `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, the generated instruction table is registered by `pkg/ifuzz/riscv64/generated` and used by syzkaller instruction fuzzing to enumerate and instantiate RISC-V encodings. The assembly operands `vd, vs2, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vd` bits 11-7] for generated operands to be meaningful.

## Risks and Edge Cases

mask destination/source aliasing and vstart handling matter architecturally but are not represented in generated fields the generator ignores description, long_name, data_independent_timing, most access modes, and Sail code, so YAML schema drift can silently reduce semantic coverage while still producing an instruction entry

## Test Signals

run the RISC-V ifuzz generator over this YAML tree and confirm the generated `Insn` keeps this mnemonic, opcode, mask, and decoded fields; compare against Sail/spec execution for representative legal and illegal vector configurations; cover mask inactive/tail behavior and vstart reset.
