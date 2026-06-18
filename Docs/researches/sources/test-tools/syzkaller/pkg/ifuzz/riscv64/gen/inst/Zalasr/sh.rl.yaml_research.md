# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalasr/sh.rl.yaml

Source read: complete local YAML (78 lines). Descriptor summary: `kind: instruction`, `name: sh.rl`, `long_name: No synopsis available`.

## Purpose

`sh.rl.yaml` is a Zalasr descriptor for `sh.rl`, a release store halfword instruction with assembly form `xs2, (xs1)`. It uses `xs1` as address base and `xs2` as the store value. The descriptor text is sparse (`long_name` and `description` are placeholders), but the instruction name, match string, variables, and Sail snippet identify it as part of the acquire-load/release-store family.

## Important APIs, Types, and Functions

This file is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The current Go generator reads only the top-level instruction kind, name, 32-bit match string, encoding variables, and U/VU access flags. The match string is `0011101----------001000000101111` with 22 fixed bits and 10 operand bits. Generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`. The `operation()` block is empty, while the Sail block contains the load/store address translation, alignment, memory access, and exception flow.

## Control Flow

During table generation, `WalkDir` reads this YAML, `buildInsn` converts fixed bits into opcode/mask values, and `parseLocations` accepts the register ranges because they are in `hi-lo` form. At fuzzing time ifuzz can vary the listed registers while preserving the fixed Zalasr opcode, width, and ordering bits. Architecturally, the Sail path computes an address from `rs1` plus an immediate-like zero offset, performs extension address checks, checks alignment, translates the address, and then performs a release memory write of the selected width. The local generator does not execute or validate that Sail control flow.

## State and Persistence Behavior

The YAML itself is static. Its persistent generated state is a `riscv64.Insn` row containing `sh.rl`, opcode/mask metadata, field ranges, and non-privileged classification because access is s=always, u=always, vs=always, vu=always. Runtime architectural state is memory at the address based on `xs1`; the instruction writes the low operand bits from `xs2` to memory and has no destination register. `data_independent_timing: false` is present in the descriptor, but the local generator ignores it, so timing metadata is not persisted into ifuzz output.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema and the Zalasr extension. Locally it integrates with the RISC-V ifuzz generator, `riscv64.InsnField`, and the generated instruction registry. Extension metadata says `Zalasr`. The Sail block is the only substantive semantic source in this file because the prose and `operation()` fields are placeholders; downstream consumers that need semantics must either read Sail or obtain them from the architecture spec.

## Risks and Edge Cases

The biggest risk is semantic sparseness: placeholder synopsis/description plus an empty `operation()` block mean reviewers cannot rely on unified-db pseudocode here. The generator still emits an instruction from the encoding alone, so a malformed Zalasr semantic block would not affect ifuzz generation. The Sail snippet appears generic and references an offset/`imm` even though the assembly has no immediate operand, which is acceptable as template inheritance but worth checking against the final ISA definition. Encoding risk is concentrated in funct3 `001` for halfword, fixed acquire/release prefix bits, and for stores the fixed zero destination/register field in the match string.

## Test Signals

Regenerate `generated/insns.go` and assert `sh.rl` appears with match `0011101----------001000000101111` and fields `xs2` at `24-20`; `xs1` at `19-15`. Encode/decode tests should randomize all listed source/destination registers and verify fixed width/order bits remain unchanged. Add family tests across `lb/lh/lw/ld.aq` and `sb/sh/sw/sd.rl` to catch funct3 or operand-field swaps. Semantic validation should use an ISA simulator or Sail oracle because local ifuzz table generation does not check the empty `operation()` block, placeholder descriptions, alignment behavior, or acquire/release memory effects.
