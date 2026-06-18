<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/C/c.ld.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/C/c.ld.yaml

## Purpose

`c.ld.yaml` is a riscv-unified-db YAML descriptor for the `c.ld` instruction. It is a `instruction` entry in the `C` instruction subset and represents a compressed memory access operation. Its long name is "Load double". The description says: Loads a 64-bit value from memory into register xd. It computes an effective address by adding the zero-extended offset, scaled by 8, to the base address in register xs1. It expands to `ld` `xd, offset(xs1)`. For RV32, if the Zclsd extension is enabled, this instruction loads a 64-bit value into registers xd and xd+1...

## Important APIs, Types, and Functions

The file is data consumed by `pkg/ifuzz/riscv64/gen/gen.go`, not executable code. The generator unmarshals it into `instYAML`, reading `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. For this descriptor, `definedBy` resolves to `Zca, Zclsd`, the assembly form is `xd, imm(xs1)`, and the encoded variable fields are: No variable fields are declared; all encoding bits are fixed by the match pattern.

## Control Flow

During generation, `filepath.WalkDir` finds this YAML file, `yaml.Unmarshal` populates the instruction metadata, and `buildInsn` converts the match string into an opcode and mask. The source does not expose an `encoding.match` pattern, so the generator would skip it. Each declared variable range is passed through `parseLocations`; split locations produce multiple `InsnField` entries with suffixed names so the fuzzer can fill discontiguous bitfields. If the match length is not 32 bits, the current generator skips the file, which is relevant for compressed 16-bit descriptors.

## State and Persistence Behavior

This source has no runtime state or persistence of its own. Its persistent effect is indirect: when accepted by the generator, it contributes one `riscv64.Insn` to the generated Go table, with `Name=c.ld`, fixed opcode/mask bits from the match pattern, generated fields from the variable list, `AsUInt32` initialized to the opcode, and `Priv` derived from access mode. The YAML includes semantic text but the current generator persists only encoding, name, fields, and privilege state.

## Dependencies and Integration Points

The descriptor depends on the riscv-unified-db schema (`inst_schema.json`) and is integrated through `gopkg.in/yaml.v3` unmarshalling in `gen.go`. The generated table imports `github.com/google/syzkaller/pkg/ifuzz/riscv64` and registers instructions with syzkaller's RISC-V ifuzz backend. Architectural integration is through `Zca, Zclsd` extension availability, privilege access `s=always, u=always, vs=always, vu=always. The generator treats this as non-privileged because U/VU access is not `never`.`, and any operation/Sail snippets kept in the source for humans or future tooling.

## Risks and Edge Cases

The main risk is schema drift: fields such as `left_shift`, `not`, richer `definedBy` constraints, and semantic snippets are not modeled by `instYAML`, so they do not affect fuzz generation. A malformed or non-32-bit match pattern silently drops the instruction. Discontiguous immediate fields rely on range ordering from the YAML and simple `hi-lo` parsing, so encodings with single-bit locations or nonstandard location syntax may be skipped unless the generator is extended. Privilege classification is coarse because only U/VU `never` is checked. For this file, match length is 0, fixed bits are 0, variable bits are 0, and privileged classification is False.

## Test Signals

Good signals are generator tests that include this file, assert that `c.ld` appears or is intentionally skipped, and compare the generated opcode/mask/field list against the YAML. Decode/encode round trips in `pkg/ifuzz/riscv64` should validate that randomized operands preserve fixed bits. `operation()` is present and starts with `if (implemented?(ExtensionName::C) && (CSR[misa].C == 1'b0)) { raise(ExceptionCode::IllegalInstructi`. A Sail semantic snippet is also embedded for architecture-model traceability. Privilege tests should confirm that access modes map to the expected `Insn.Priv` value and that compressed or reserved encodings are handled intentionally.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/C/c.ld.yaml -->
