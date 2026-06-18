<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.rl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.rl.yaml

## Purpose

`amomaxu.w.rl` is an auto-generated riscv-unified-db instruction descriptor for the RISC-V `Zaamo` atomic memory-operation extension. It describes `Atomic MAX unsigned word (release)` using the common AMO assembly form `xd, xs2, (xs1)`: load the word at the address in `xs1`, return the loaded value through `xd`, combine the loaded value with `xs2` using unsigned maximum, and store the result back to the same address. This specific variant uses `release` ordering and comes from `spec/std/isa/inst/Zaamo/amomaxu.SIZE.AQRL.layout`.

## Important APIs, Types, and Functions

The source is declarative YAML consumed by `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go` through the local `instYAML` type, not Go code executed directly. The generator reads `kind`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. This file sets `kind: instruction`, `name: amomaxu.w.rl`, and `encoding.match: 1110001----------010-----0101111` with 17 fixed bits and 15 operand bits. Its declared fields are `xs2` at `24-20`; `xs1` at `19-15`; `xd` at `11-7`; these become `riscv64.InsnField` entries after `parseLocations`. The semantic `operation()` block calls `amo<32>(virtual_address, X[xs2][31:0], AmoOperation::Maxu, 1'b0, 1'b1, $encoding);`, which selects `AmoOperation::Maxu`, width `32`, acquire bit `0`, and release bit `1`. `X[xs2][31:0]` is passed to the 32-bit AMO helper, and the loaded word is sign-extended into `xd` by AMO semantics.

## Control Flow

During table generation, `filepath.WalkDir` discovers this `.yaml` file, `yaml.Unmarshal` fills `instYAML`, `main` skips non-instruction or non-32-bit encodings, and `buildInsn` converts the `match` string into an opcode and mask. `buildInsn` then parses the variable ranges and marks the resulting instruction as privileged only when user or virtual-user access is `never`; here the access map is `s=always`, `u=always`, `vs=always`, `vu=always`, so the generated `Insn.Priv` value is false. Architecturally, the descriptor's `operation()` first checks that extension `A` is implemented and not disabled by `misa.A`, raises `IllegalInstruction` otherwise, then optionally runs memory-model hooks (memory_model_release() after the AMO helper), reads `X[xs1]` as the virtual address, invokes the AMO helper, writes the helper return value into `X[xd]`, and runs the release hook when present.

## State and Persistence Behavior

The YAML file has no mutable runtime state and performs no persistence itself. Its persistent effect is the generated instruction-table entry: `Name=amomaxu.w.rl`, opcode/mask derived from `1110001----------010-----0101111`, operand fields for `xs2`, `xs1`, and `xd`, initial `AsUInt32` equal to the fixed opcode, and non-privileged access classification. The semantic text describes architectural state transitions over integer registers, memory, and memory-ordering barriers, but the current syzkaller generator does not persist `definedBy`, `description`, `operation()`, or `sail()` into the generated Go table.

## Dependencies and Integration Points

This descriptor depends on the riscv-unified-db instruction schema (`inst_schema.json#`) and on the `Zaamo`/`A` atomic extension model. The descriptor is gated by `definedBy: extension: Zaamo`; the word form is available without an explicit XLEN-only constraint in this YAML. In the generator path, it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated package registration that calls `Register(insns_riscv64)`. In the architecture-model path, `amomaxu.w.rl` relies on the shared AMO helper, memory model acquire/release helpers, `CSR[misa]`, exception raising, and the Sail memory primitives `ext_data_get_addr`, `translateAddr`, `mem_read`, and `mem_write_value`. The embedded Sail block models address derivation, translation, early write-effect checks, memory read, AMO result calculation, write-back, exception handling, and retirement success/failure.

## Risks and Edge Cases

The main integration risk is semantic loss: syzkaller's generator currently uses only the encoding/name/access subset, so it will fuzz the instruction bits but will not understand the AMO operation, acquire/release ordering, XLEN constraint, alignment behavior, exception behavior, or signedness from the YAML semantics. For this file, correctness-sensitive details include the `Maxu` operation (uses unsigned comparison between the loaded value and rs2), the `32`-bit memory width, and acquire/release flags `0/1`. Word forms rely on using only the low 32 bits of `xs2` and sign-extending the loaded word into `xd`; doubleword forms require RV64 and should not be emitted for RV32. The Sail snippet also shows translation failures, memory exceptions, and unexpected width combinations as important failure paths that are outside the current fuzzer table representation.

## Test Signals

Useful tests should assert that the generator includes `amomaxu.w.rl` with match `1110001----------010-----0101111`, fields `xs2@24-20`, `xs1@19-15`, and `xd@11-7`, and `Priv=false`. Encoding round-trip tests should confirm randomized operands preserve the fixed AMO opcode bits and ordering bits. Architecture-facing tests should exercise `Maxu` over representative loaded and `xs2` values, including signed or unsigned comparison boundaries where relevant, and should verify `release` memory-order behavior by checking the acquire/release hooks in the semantic model. RV64 gating should be tested for doubleword descriptors, while word descriptors should test low-32-bit operand handling and sign-extension of the returned loaded word.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zaamo/amomaxu.w.rl.yaml -->
