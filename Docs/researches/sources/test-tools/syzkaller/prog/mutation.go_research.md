## sources/test-tools/syzkaller/prog/mutation.go

Purpose: implements program mutation for syzkaller programs, including whole-program operations and per-argument mutations. It is the main fuzzing evolution engine after generation.

Important APIs/types/functions: `Prog.Mutate`, `Prog.MutateWithOpts`, `MutateOpts`, `mutator`, `splice`, `squashAny`, `insertCall`, `removeCall`, `mutateArg`, `chooseCall`, `Target.mutateArg`, per-type `mutate` methods, `mutationArgs`, mutation-priority methods, `mutateData`, `loadInt`, `storeInt`, and endian swap helpers.

Control flow: `MutateWithOpts` builds a `randGen`, normalizes the call limit, then repeatedly selects a weighted operation until the expected-iteration stop condition fires. Insert and argument mutation analyze existing state before generating support calls, splice clones corpus programs, removal fixes resource users through `RemoveCall`, and final `sanitizeFix` plus debug validation enforce invariants.

State and persistence: all state is in-memory on `Prog`, `Call`, and `Arg` graphs. Resource use links are updated via `replaceArg`, `removeArg`, and `replaceResultArg`. Blob and compressed-image mutations alter `DataArg` data, and pointer allocations may move when pointee size grows.

Dependencies/integration: depends on `rand.go` generation, `state` analysis, `size.go` length assignment, `image` compression for filesystem images, choice-table selection from `prio.go`, and type definitions from `types.go`.

Risks: mutation relies on correct resource link repair; a missed `removeArg` can leave dangling users. Compressed-image mutation must not target empty decompressed data. Size mutations intentionally make invalid lengths but must preserve decompression safety. A notable risk in nearby generation logic used by mutation is `resourceCentric` in `rand.go`, where a biased length is calculated from `len(calls)` even though the local `calls` slice is nil, which can panic if that path is reached.

Test signals: `mutation_test.go` checks flags, argument priority, no-squash behavior, length mutation bounds, clone immutability, corpus mutation, table-driven mutation goals, negative mutations, and store/load helpers.
