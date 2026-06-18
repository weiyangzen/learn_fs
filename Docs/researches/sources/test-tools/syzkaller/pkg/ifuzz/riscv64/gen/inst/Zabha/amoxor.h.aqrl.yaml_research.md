# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zabha/amoxor.h.aqrl.yaml

Source read: complete local YAML (146 lines). Descriptor summary: `kind: instruction`, `name: amoxor.h.aqrl`, `long_name: Atomic fetch-and-xor halfword (acquire-release)`.

## Purpose

`amoxor.h.aqrl.yaml` is a riscv-unified-db instruction descriptor for `amoxor.h.aqrl`, the Zabha atomic fetch-and-xor halfword instruction. The assembly form is `xd, xs2, (xs1)`: `xs1` supplies the target address, `xs2` supplies the source operand, and `xd` receives the sign-extended value loaded from memory before the update. The descriptor states that the instruction atomically reads a halfword, computes the bitwise XOR result, and writes the low 16 bits back to the same address.

## Important APIs, Types, and Functions

This YAML is declarative input to `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`. The Go generator unmarshals it into `instYAML` and consumes `kind`, `name`, `encoding.match`, `encoding.variables`, and the U/VU access flags; descriptions, `definedBy`, `operation()`, and Sail are retained as source evidence but are not executed by ifuzz. The encoding match is `0010011----------001-----0101111` with 17 fixed bits and 15 operand bits. The generator-visible variables are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. The operation block calls `amo<16>(virtual_address, X[xs2][15:0], AmoOperation::Xor, 1'b1, 1'b1, $encoding)` after checking atomic extension availability; the acquire/release arguments are fixed by this descriptor's suffix rather than represented as operand variables.

## Control Flow

Generation control starts from `go generate` in `pkg/ifuzz/riscv64`, which runs `go run gen/gen.go gen/inst generated/insns.go`. `filepath.WalkDir` reaches this YAML, `yaml.Unmarshal` fills the partial `instYAML`, `buildInsn` converts the 32-character match string into `OpcodeMask` and `Opcode`, and `parseLocations` turns the three register ranges into `riscv64.InsnField` entries. At fuzzing time the generated `Insn` template randomizes `xs2`, `xs1`, and `xd` bits while preserving the fixed AMO opcode/funct fields. Architecturally, the pseudocode reads `X[xs1]`, performs the atomic memory operation with acquire-release ordering; the match string fixes both ordering bits high, and operation pseudocode calls acquire before the memory action and release after it, stores the old memory value into `X[xd]`, and relies on the shared AMO/Sail paths for memory translation and exception behavior.

## State and Persistence Behavior

The YAML itself has no mutable state. Its persistent local effect is a generated `riscv64.Insn` entry in `generated/insns.go` containing the instruction name, opcode/mask pair, field ranges, initial `AsUInt32`, and non-privileged access classification. Runtime state touched by the modeled instruction is architectural memory at `X[xs1]` and integer register `xd`; the Sail snippet models address translation, memory exception propagation, sign extension of the loaded halfword, and the atomic read-modify-write update. Since access is s=always, u=always, vs=always, vu=always, `gen.go` will not mark this entry as privileged.

## Dependencies and Integration Points

The file follows `inst_schema.json` and is auto-generated from the upstream RISC-V unified-db AMO layouts. It integrates locally with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, the generated `Register(insns_riscv64)` table, and `ParseInsn`/ifuzz instruction selection. Extension metadata says `Zabha`; operation pseudocode also checks the base atomic `A` extension and `misa.A` before performing the AMO. The Sail block is copied from the RISC-V Sail model and is the richest semantic oracle for load, write-enable, exception, and sign-extension behavior, but the current syzkaller generator does not consume it.

## Risks and Edge Cases

The main risk is metadata drift between the upstream semantic blocks and the small subset of fields consumed by `gen.go`. The generator does not validate `definedBy`, so an unavailable Zabha implementation is still fuzzable once the descriptor is generated. It also ignores the semantic check for `A`/`misa.A`, alignment and memory model subtleties from Sail, and any future schema fields. Encoding risk is concentrated in the fixed funct7/ordering bits and funct3 width bits: `001` selects halfword, while the high fixed bits distinguish `amoxor` and the ordering suffix. A wrong match string would silently generate a different instruction even though the descriptive text remained correct.

## Test Signals

Regenerate `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go` and assert that `amoxor.h.aqrl` is present with match `0010011----------001-----0101111` and fields `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`. Add encode/decode round trips that randomize all three registers and verify fixed bits remain unchanged. Family tests should compare `amoxor.h.aqrl` against the neighboring `.aq`, `.rl`, `.aqrl`, byte, and halfword descriptors so only ordering and width bits differ. Semantic validation should use an ISA simulator or Sail-derived oracle for sign extension, old-value return, and atomic memory update behavior because local ifuzz generation checks only encodings.
