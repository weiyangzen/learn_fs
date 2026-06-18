# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amoadd.w.yaml

## Purpose

`amoadd.w.yaml` describes `amoadd.w`, a Zaamo atomic fetch-and-add word descriptor with unordered memory-ordering bits, for the Zaamo atomic instruction corpus consumed by syzkaller's riscv64 ifuzz generator. It is declarative instruction data rather than executable Go code; the key payload is the mnemonic, assembly operands `xd, xs2, (xs1)`, access metadata, 32-bit encoding pattern, variable operand fields, and any embedded operation/Sail reference semantics.

## Important APIs, Types, and Functions

Schema-facing fields are `$schema=inst_schema.json#`, `kind=instruction`, `name=amoadd.w`, `assembly=xd, xs2, (xs1)`, `encoding.match=0000000----------010-----0101111`, `encoding.variables=[`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]`, `access=s=always, u=always, vs=always, vu=always`, and `data_independent_timing=not declared`. `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` maps these fields through `instYAML`, `buildInsn`, `parseLocations`, and `parseRange` into a `riscv64.Insn` containing `Name`, `OpcodeMask`, `Opcode`, `Fields`, `AsUInt32`, and `Priv`. For this descriptor the computed opcode is `0x0000202f`, the opcode mask is `0xfe00707f`, and the match string has 17 fixed bits. The embedded `sail()` block is reference semantics; notable helper calls include `extension`, `X`, `ext_data_get_addr`, `ReadWrite`, `Ext_DataAddr_Error`, `ext_handle_data_check_error`, `Ext_DataAddr_OK`, `translateAddr`, `TR_Failure`, `handle_mem_exception`, `TR_Address`, `MemoryOpResult`, `mem_write_ea`, `internal_error`, `MemException`, `MemValue`, `extend_value`, `mem_read`. The executable `operation()` block is present and semantically meaningful.

## Control Flow

Generation control flow is uniform for this file: `gen.go` walks the instruction tree, reads the YAML, unmarshals it with `gopkg.in/yaml.v3`, skips non-instruction records and non-32-bit match strings, converts fixed encoding bits into opcode/mask values, expands variable bit ranges into `InsnField` entries, marks the instruction privileged only when `u` or `vu` access is `never`, and serializes the instruction table into generated Go. The executable `operation()` block first checks that extension `A` is implemented and enabled in `misa`, applies acquire/release hooks according to the suffix, reads the virtual address from `xs1`, and calls `amo<width>` with `AmoOperation::Add` or `AmoOperation::And`. The Sail block expands that into address-extension checks, translation, effective-address write notification, memory read, operation-specific result computation, memory write, sign extension of word return values, exception handling, and final writeback to `rd`.

## State and Persistence Behavior

The YAML file has no mutable runtime state. Its persistent repository effect is the generated instruction-table entry normally emitted into `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go`, where `amoadd.w` becomes immutable decode/fuzzing metadata registered by package init. Architectural state referenced by the semantic text is external to the YAML: vector registers, mask registers, `vl`, `vstart`, memory side effects, scalar integer registers, AMO ordering state, or exception state depending on the instruction family. None of that architectural state is persisted by the YAML generator itself.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db `inst_schema.json` shape and the local syzkaller ifuzz generator. The direct repository integration points are `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, `gopkg.in/yaml.v3`, `serializer.Write`, `osutil.WriteFileAtomically`, and the `pkg/ifuzz/riscv64` instruction model. Downstream, `pkg/ifuzz/riscv64/generated` registers the generated table for instruction fuzzing and decode checks. The assembly operands `xd, xs2, (xs1)` must remain consistent with the variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7]; otherwise generated operand randomization can produce encodings that decode but do not match the intended assembler form.

## Risks and Edge Cases

The generator ignores `description`, `long_name`, most `definedBy` details, `data_independent_timing`, executable `operation()` text, and embedded Sail semantics, so schema or semantic drift can still produce a syntactically valid decode entry. AMO descriptors are sensitive to aq/rl bit placement, word versus doubleword width, RV64-only gating for `.d`, sign-extension of word return values, address translation exceptions, memory ordering hooks, and the fact that `definedBy` names `Zaamo` while the operation checks extension `A`.

## Test Signals

Run the RISC-V ifuzz generator over the instruction tree and confirm `amoadd.w` appears with match `0000000----------010-----0101111`, variable fields [`xs2` bits 24-20, `xs1` bits 19-15, `xd` bits 11-7], opcode `0x0000202f`, and mask `0xfe00707f`. Add encode/decode round-trip checks that randomize only declared operand fields and preserve all fixed bits. Semantic regression tests should cover aq, rl, aqrl, and unordered variants, word versus doubleword width, extension gating, misaligned/faulting addresses, loaded-value return behavior, and add/and memory update results.
