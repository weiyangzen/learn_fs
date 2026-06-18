# sources/test-tools/syzkaller/tools/syz-mutate/mutate.go

## Purpose
`syz-mutate` generates a random syzkaller program or mutates an input program, optionally using comparison hints for a specific call.

## Important APIs, types, and functions
- Flags select OS/arch, seed, target program length, enabled syscall list, corpus file, hint call/src/cmp values, and strict deserialization.
- `main` loads the `prog.Target`, resolves enabled syscalls with `mgrconfig.ParseEnabledSyscalls`, reads corpus with `db.ReadCorpus`, builds a choice table, and either `Generate`s or mutates a `prog.Prog`.
- Hint mode builds a `prog.CompMap` and uses `Prog.MutateWithHints` to print every hinted mutation.

## Control flow
If `-enable` is set, syscall names are parsed and transitive requirements are applied through `target.TransitivelyEnabledCalls`, with disabled calls logged to stderr. Seed defaults to current nanoseconds unless specified. With no positional argument, a fresh program is generated. With an input file, it is deserialized under strict or non-strict mode, then either hint-mutated or generally mutated.

## State and persistence behavior
The tool reads an optional corpus DB and optional input program. It writes generated programs to stdout and diagnostics to stderr. No files are modified.

## Dependencies and integration points
It uses `prog` core generation/mutation APIs, `pkg/db` corpus loading, `pkg/mgrconfig` syscall selection, and the blank `sys` import to register target descriptions.

## Risks and edge cases
Randomness is reproducible only when `-seed` is specified. Empty corpus path behavior depends on `db.ReadCorpus`. Hint mode prints multiple programs and returns without printing the final original/mutated program. Type correctness and call availability are delegated to `prog` APIs.

## Test signals
No direct tests. Useful checks are fixed-seed golden generation, strict vs non-strict parse failures, enabled syscall filtering, and hint mutation output count/shape.
