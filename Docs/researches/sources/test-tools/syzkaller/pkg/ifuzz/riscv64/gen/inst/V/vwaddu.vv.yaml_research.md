# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vwaddu.vv.yaml

## Purpose

`vwaddu.vv.yaml` describes `vwaddu.vv`, a unsigned widening add, for the RISC-V Vector (`V`) instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `vd, vs2, vs1, vm`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=vwaddu.vv`, `assembly=vd, vs2, vs1, vm`, `encoding.match=110000-----------010-----1010111`, `encoding.variables=[`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=true`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0xc0002057`, the opcode mask is `0xfc00707f`, and the match string has 16 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `get_sew`, `get_lmul_pow`, `get_num_elem`, `illegal_variable_width`, `not`, `valid_reg_overlap`, `handle_illegal`, `vector`, `read_vmask`, `bits`, `read_vreg`, `init_masked_result`, `to`, `write_vreg`. The `operation()` block is empty in this descriptor.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The Sail block computes SEW_widen and LMUL_widen, validates widening destination width and overlap for both narrow sources, reads mask/source/destination vectors, initializes masked wide results, performs signed or unsigned widening add/subtract/multiply per active element, writes the widened destination group, and clears `vstart`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `vwaddu.vv` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `vd, vs2, vs1, vm` must remain consistent with the variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. Widening and extension instructions are especially sensitive to SEW/LMUL legality, widened destination register grouping, fractional source grouping, valid overlap rules, `vl=0` reduction behavior, signed versus unsigned interpretation, and masked inactive/tail behavior.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `vwaddu.vv` appears with match `110000-----------010-----1010111`, variable fields [`vm` bits 25-25, `vs2` bits 24-20, `vs1` bits 19-15, `vd` bits 11-7], opcode `0xc0002057`, and mask `0xfc00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Widening tests should cover SEW/LMUL boundaries, overlap legality, signed and unsigned operands, scalar forms, mask/tail policies, and destination group sizing.
