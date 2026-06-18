## sources/test-tools/syzkaller/prog/rand.go

Purpose: implements random program, call, argument, resource, filename, buffer, text, and pseudo-syscall generation.

Important APIs/types/functions: `randGen`, `newRand`, probability helpers, `randInt`, `truncateToBitSize`, `flags`, filename/string generators, allocation helpers, recursion pruning, `createResource`, `generateText`, `generateCall`, `generateParticularCall`, `Target.GenerateAllSyzProg`, `PseudoSyscalls`, `GenSampleProg`, `DataMmapProg`, `generateArgs`, `generateArgImpl`, and per-type `generate` methods.

Control flow: generation chooses calls from a `ChoiceTable`, creates a `Call`, recursively generates typed arguments, patches conditional fields, assigns sizes, and returns prerequisite calls before the final call. Resource generation prefers existing resources, then corpus-derived/resource-centric resources, then constructors, then special constants. Buffer and text generation use kind-specific strategies.

State and persistence: uses in-memory `state` for resources, files, strings, memory allocation, VMA allocation, corpus, and choice table. `randGen` tracks recursion depth and KFuzzTest/resource-generation modes.

Dependencies/integration: integrates with `prio.go`, `resources.go`, `size.go`, `mutation.go`, ifuzz, image compression, target special type hooks, and memory allocation utilities.

Risks: recursive type generation must be bounded to avoid exponential trees. Filename generation must not escape the sandbox. Resource construction can generate support calls and requires correct state analysis. The `resourceCentric` function appears to compute `biasedLen` from `len(calls)` rather than `len(p.Calls)`, making the path vulnerable to a negative argument to `biasedRand`.

Test signals: `rand_test.go`, `resources_test.go`, `prog_test.go`, and fuzz tests cover determinism, enabled/no-generate constraints, integer bounds, filenames, resource creation, and serialization.
