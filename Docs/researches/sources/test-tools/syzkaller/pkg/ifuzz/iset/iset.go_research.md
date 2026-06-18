# sources/test-tools/syzkaller/pkg/ifuzz/iset/iset.go

## Purpose
`iset.go` defines the shared instruction-set interfaces, configuration model, architecture registry, mode/type taxonomy, and integer-generation helper used by syzkaller's instruction fuzzer backends.

## Important APIs, Types, And Functions
Architecture constants identify registered backends: `ArchX86`, `ArchPowerPC`, `ArchArm64`, and `ArchRiscv64`. `Arches` is the global `map[string]InsnSet` populated by generated architecture packages. `Mode` and `Type` are small integer enums. `Insn` requires `Info() (name, mode, pseudo, priv)` and `Encode(cfg, r)`. `InsnSet` requires `GetInsns`, `Decode`, and `DecodeExt`. `Config` controls architecture, generated instruction count, mode, privileged generation, execution-oriented generation, and memory regions. `MemRegion` describes target memory ranges for generated immediates. `ModeInsns` is the per-mode/per-type instruction index. `(*ModeInsns).Add`, `(*Config).IsCompatible`, and `GenerateInt` are the important helpers.

## Control Flow
Architecture packages call `ModeInsns.Add` while registering each instruction. `Add` reads `Insn.Info`, iterates all modes, skips unsupported modes by testing the instruction's mode bitmask, and appends pseudo instructions to `TypeExec`, privileged instructions to `TypePriv` and `TypeAll`, and normal instructions to `TypeUser` and `TypeAll`. `Config.IsCompatible` performs the inverse compatibility check for one instruction against a config, panicking on invalid modes and rejecting privileged, pseudo, or mode-incompatible instructions as needed.

`GenerateInt` validates the requested byte size, chooses among several random value families, optionally biases values toward configured memory regions, occasionally negates the result, and occasionally clears low page-offset bits for sizes larger than one byte. Its output is a fuzzing-biased integer rather than a uniform integer.

## State And Persistence Behavior
`Arches` is mutable global process state and is the main registration point for all backends. `ModeInsns` instances are built during registration and then treated as read-mostly indexes. `Config` and `MemRegion` are caller-owned values. There is no persistent storage; all behavior is in-memory and random-source driven.

## Dependencies And Integration Points
The file depends only on `math/rand`. It is imported by the top-level `ifuzz` package and every architecture backend. Generated architecture packages indirectly rely on `ModeInsns.Add` classification to make `randInsn` work. `GenerateInt` is available to architecture-specific generators that need biased immediates or addresses.

## Risks And Edge Cases
`Arches` is a plain map with init-time mutation and no synchronization; it is safe for normal package initialization but not designed for dynamic concurrent registration. `ModeInsns.Add` classifies pseudo instructions only as `TypeExec`, so pseudo instructions are absent from `TypeAll`; callers need to request exec explicitly. `Config.IsCompatible` panics on invalid `Mode`, while other call paths may panic less clearly if a mode or architecture lacks instructions. `SpecialNumbers` contains `1 << 47` twice, intentionally or accidentally increasing that value's weight. `GenerateInt` can panic for invalid sizes and can modulo by `mem.Size`, so callers should not pass zero-sized memory regions.

## Test Signals
`ifuzz_test.go` exercises `ModeInsns` classification through `GetInsns`, encode/decode compatibility, and generated stream decoding for all registered architectures. Additional focused tests could cover `Config.IsCompatible`, `GenerateInt` distribution boundaries, memory-region biasing, zero-sized memory regions, and the intended classification of pseudo versus privileged instructions.
