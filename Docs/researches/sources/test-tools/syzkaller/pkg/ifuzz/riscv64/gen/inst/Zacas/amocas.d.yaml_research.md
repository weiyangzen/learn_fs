# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zacas/amocas.d.yaml

Source read: complete local YAML (134 lines). Descriptor summary: `kind: instruction`, `name: amocas.d`, `long_name: Atomic compare-and-swap doubleword`.

## Purpose

`amocas.d.yaml` describes `amocas.d`, the Zacas atomic compare-and-swap doubleword instruction. The assembly form is `xd, xs2, (xs1)`. Architecturally it loads the doubleword at `X[xs1]`, writes the loaded value to `xd`, compares the loaded value with `xs2`, and on success writes the replacement value held in `xd` or the paired replacement operand described by the upstream spec text. No acquire/release suffix; the ordering bits are fixed low or absent for this encoded form.

## Important APIs, Types, and Functions

For local syzkaller ifuzz, this YAML is consumed by `riscv64/gen/gen.go` through the partial `instYAML` struct. The generator-visible fields are the instruction `name`, top-level `encoding.match`, top-level `encoding.variables`, and U/VU access flags. The match string is `0010100----------011-----0101111`, with 17 fixed bits and 15 operand bits; variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The `operation()` block currently contains a semantic TODO and a commented call to `amocas64(virtual_address, ..., aq, rl, $encoding)`, so it documents intended behavior but is not a complete executable pseudocode model.

## Control Flow

The generation path walks the YAML tree, ignores non-instruction files, requires a 32-character match string, builds opcode and mask bits from `0`/`1`, and turns each register range into `InsnField` metadata. This descriptor is compatible with that path because all generator-visible variable locations are `hi-lo` ranges. At architectural level, the operation first checks `implemented?(ExtensionName::Zacas)`, applies acquire and/or release memory-model hooks according to the suffix, reads `X[xs1]` as the virtual address, and then stops at the TODO placeholder. The Sail snippet supplies the detailed compare/read/write control flow: address translation, memory exception handling, loaded-value comparison, conditional write on success, no write on compare failure, and `X(rd)` update with the loaded value.

## State and Persistence Behavior

The file has no mutable repository state, but a successful generation persists an `Insn` table row in `generated/insns.go`. The generated row controls ifuzz byte emission and decode matching; it does not persist the compare-and-swap algorithm. Runtime architectural state represented by the spec includes memory at `X[xs1]`, register `xd` as both result destination and replacement source in the CAS model, and register `xs2` as the compare source. Access is s=always, u=always, vs=always, vu=always, so the generator classifies the instruction as non-privileged.

## Dependencies and Integration Points

The descriptor depends on the RISC-V unified-db `inst_schema.json`, the Zacas extension definition, and the shared AMO major opcode encoding. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the `Register(insns_riscv64)` initialization path used by `pkg/ifuzz`. Extension metadata says `Zacas`. The Sail section is an upstream semantic oracle, but `gen.go` ignores it and cannot catch TODOs or width-specific semantic gaps.

## Risks and Edge Cases

The explicit TODO in `operation()` is the highest semantic risk: the local encoding generator will still emit `amocas.d` even though the unified-db operation block is incomplete. The Sail block is generic and valuable, but quadword forms need extra scrutiny because the visible Sail width dispatch is narrower than the descriptor's 128-bit intent. The generator ignores `definedBy`, so RV64-only constraints for `.q` forms are not enforced by the generated `Insn` metadata. Encoding risk is around funct3 `011` for doubleword and high fixed bits that encode acquire/release ordering. If Zacas semantics later change from `xd` replacement to an adjacent-register replacement convention, the descriptive text, TODO helper signature, and Sail text must be reconciled together.

## Test Signals

Regenerate the RISC-V ifuzz table and assert that `amocas.d` is present with opcode match `0010100----------011-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add round-trip tests that randomize `xs2`, `xs1`, and `xd` while fixed bits remain stable. Add family-difference tests across `.w`, `.d`, `.q`, `.aq`, `.rl`, and `.aqrl` forms so only width and ordering bits move. Semantic tests should be external to current ifuzz generation: execute CAS success and failure cases under a RISC-V model and check `xd`, memory write/no-write behavior, acquire/release ordering annotations, and RV64-only treatment for quadword descriptors.
