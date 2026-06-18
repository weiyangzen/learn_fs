# sources/test-tools/syzkaller/pkg/ifuzz/ifuzz.go

## Purpose
`ifuzz.go` is the public architecture-neutral facade for syzkaller's instruction fuzzer. It re-exports core configuration types and architecture/mode constants, imports generated architecture backends for registration, generates random instruction streams, mutates existing byte streams, and splits byte streams into decoder-recognized instruction-sized chunks.

## Important APIs, Types, And Functions
The file aliases `iset.Config`, `iset.MemRegion`, and `iset.Mode`, and re-exports architecture and mode constants such as `ArchX86`, `ArchArm64`, and `ModeLong64`. `Generate(cfg, r)` emits `cfg.Len` instructions. `Mutate(cfg, r, text)` applies random instruction-level and byte-level changes. `randInsn(cfg, r)` chooses an instruction compatible with privilege and execution settings. `split(cfg, text)` uses the architecture decoder to divide byte text into known instruction chunks and runs of undecodable bytes.

The blank imports for `arm64/generated`, `powerpc/generated`, `riscv64/generated`, and `x86/generated` are part of the API surface because they populate `iset.Arches` during package initialization.

## Control Flow
`Generate` loops `cfg.Len` times, selects an instruction with `randInsn`, encodes it, and appends the bytes to the output. `Mutate` first calls `split`, then repeatedly applies random mutations until a probabilistic stop condition is met and at least one mutation path has succeeded. It may delete an instruction, replace an instruction with a newly generated one, mutate bytes within an instruction-sized chunk, or insert a new generated instruction while respecting `cfg.Len` as an upper bound for insertions.

The nested byte mutation loop may delete, replace, bit-flip, or insert individual bytes until it probabilistically stops with a non-empty mutated chunk. After instruction-list mutation, `Mutate` flattens all chunks back into one byte slice. `randInsn` chooses from `TypeExec`, `TypePriv`, or `TypeUser` lists depending on `cfg.Priv` and `cfg.Exec`, then returns a random element. `split` clones the input, repeatedly asks the registered architecture decoder for the next instruction size, accumulates undecodable bytes into a `bad` chunk, and appends recognized instructions as separate chunks.

## State And Persistence Behavior
The file has no persistent storage. Runtime state flows through caller-owned `Config`, `rand.Rand`, and byte slices. `split` clones the input before slicing so returned chunks do not alias the caller's original `text`; however, chunks can share the cloned backing array with each other where they are slices of the clone. Global architecture state comes from the `iset.Arches` registry initialized by blank imports.

## Dependencies And Integration Points
`ifuzz.go` depends on `math/rand`, `slices`, and `pkg/ifuzz/iset`. It integrates with all generated architecture packages through init side effects. Callers use this package rather than architecture packages directly when they need portable generation or mutation. Architecture implementations must satisfy `iset.InsnSet` and provide non-empty instruction lists for requested modes and types.

## Risks And Edge Cases
`randInsn` assumes `iset.Arches[cfg.Arch]` exists and the selected instruction list is non-empty; bad architecture names, unsupported modes, or over-restrictive privilege/exec settings can panic through nil access or `Intn(0)`. `Mutate` has probabilistic loops, so behavior is deterministic only for a fixed random source but output length and operation count vary. Insertions are capped by instruction count, not byte size. `split` treats decoder errors and zero-size decodes as undecodable single bytes, preserving fuzz input but potentially grouping long invalid runs as one mutation unit.

## Test Signals
`ifuzz_test.go` tests mode enumeration, encode/decode round trips for all registered architectures, and generated stream decodability. These tests catch missing blank imports, empty instruction buckets, architecture decoder failures, pseudo-instruction expansion issues, and generated instruction encodings that cannot be decoded.
