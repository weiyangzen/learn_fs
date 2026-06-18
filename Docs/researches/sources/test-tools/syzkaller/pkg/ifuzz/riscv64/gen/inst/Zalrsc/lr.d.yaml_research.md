# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zalrsc/lr.d.yaml

Source read: complete local YAML (148 lines). Descriptor summary: `kind: instruction`, `name: lr.d`, `long_name: Load reserved doubleword`.

## Purpose

`lr.d.yaml` describes `lr.d`, a Zalrsc load-reserved doubleword instruction with assembly form `xd, (xs1)`. It participates in RISC-V LR/SC atomic sequences: LR establishes a reservation and returns the loaded value, while SC conditionally stores a value if the reservation is still valid and reports success/failure in `xd`. The descriptor includes extensive architecture prose about alignment, reservation sets, failure codes, and acquire/release ordering.

## Important APIs, Types, and Functions

The file is declarative input for `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/gen.go`, but it exposes a current generator limitation. Its match string is `00010--00000-----011-----0101111` with 20 fixed bits and 12 variable bits. Variables are `aq` at `26` (with not: 1); `rl` at `25` (with not: 1); `xs1` at `19-15`; `xd` at `11-7`. `aq` and `rl` are variable ordering bits, `xs1` is the address register, and `xd` is the result register. The operation block checks natural 64-bit alignment, calls `load_reserved<32>` in the current source text, and writes the reserved load result to `xd`.

## Control Flow

The intended generation flow is the same as other RISC-V descriptors: walk the YAML tree, unmarshal into `instYAML`, build opcode/mask bits, parse variable locations, and append a `riscv64.Insn`. For this file, `buildInsn` reaches `parseLocations` for `aq` at `26` and `rl` at `25`, but `parseRange` splits only `hi-lo` forms and therefore returns false for a bare single-bit location. The instruction is consequently skipped by the current generator unless single-bit locations are normalized or generator support is extended. Architecturally, the operation checks atomic availability, reads `X[xs1]`, handles misalignment with implementation-dependent exception choice, and then performs the LR/SC reservation action. The Sail block supplies the detailed memory translation, reservation matching, exception, and success/failure control flow.

## State and Persistence Behavior

If generator support is fixed, this descriptor would persist an `Insn` table row with variable `aq`/`rl` bits and register operands. In the current code path it is expected to be absent from `generated/insns.go` because of the single-bit parse limitation. Runtime architectural state includes the hart reservation state, memory at `X[xs1]`, and result register `xd`; LR has no `xs2` source operand. Access is s=always, u=always, vs=always, vu=always, so the instruction is architecturally user-visible and should not be marked privileged by ifuzz once generated.

## Dependencies and Integration Points

The descriptor depends on the unified-db instruction schema, the Zalrsc extension, and the shared RISC-V atomic memory model. Locally it integrates with `gopkg.in/yaml.v3`, `riscv64.Insn`, `riscv64.InsnField`, `serializer.Write`, and the generated ifuzz registry only after the location parser can handle single-bit variables. Extension metadata says `Zalrsc`; the operation text checks the atomic `A` architectural availability through `implemented?(ExtensionName::A)` / `misa.A`. The doubleword forms additionally require `xlen: 64` in `definedBy`. The semantic blocks reference helpers such as `load_reserved`, `store_conditional`, `is_naturally_aligned`, `LRSC_MISALIGNED_BEHAVIOR`, and Sail reservation helpers; none of these are executed by the ifuzz generator.

## Risks and Edge Cases

This descriptor is not currently consumable by `parseLocations` because `aq` and `rl` use single-bit locations (`26` and `25`) while `parseRange` accepts only `hi-lo` strings; `not: 1` is also ignored by the Go struct. That makes this file a table-coverage risk rather than just a semantic descriptor. There is also semantic complexity around misaligned LR/SC exceptions, reservation aliasing, device writes, SC failure codes, and ordering-bit combinations. For `lr.d`, the visible operation calls `load_reserved<32>` despite the doubleword name and 64-bit alignment check, which should be reviewed against the upstream source or generator import.

## Test Signals

Add a generator unit test for single-bit variable locations using this descriptor as a fixture, then assert `lr.d` is either intentionally skipped with a documented reason or generated with fields `aq` at `26` (with not: 1); `rl` at `25` (with not: 1); `xs1` at `19-15`; `xd` at `11-7`. After parser support exists, regenerate `generated/insns.go` and run encode/decode round trips over `aq`, `rl`, and register operands. Architectural tests should cover aligned success, reservation failure, misalignment exception choice, acquire/release bit combinations, and SC result values. For `lr.d`, include a targeted check that the generated/semantic width is truly 64 bits and not accidentally inherited from a 32-bit helper call.
