# sources/test-tools/syzkaller/prog/hints.go

Purpose: implements comparison-guided mutation hints that replace program argument values with values observed in executor comparison feedback.

Important APIs/types/functions: `CompMap` with `Add`, `String`, `Len`, `InplaceIntersect`; `Prog.MutateWithHints`; `generateHints`; `checkConstArg`; `checkDataArg`; `checkCompressedArg`; `shrinkExpand`; `HintsLimiter.Limit`; `specialIntsSet` initialization.

Control flow and state: `MutateWithHints` clones the program, iterates args in one call, generates candidate replacements, sanitizes and condition-checks each candidate, validates it, then invokes the callback until it returns false. Const/data checks derive replacement values through `shrinkExpand`, which models integer narrowing, sign extension, big-endian matching, bit-size limits, and special-int filtering. Compressed images are decompressed, mutated only at aligned 4/8-byte offsets, recompressed per candidate, and restored afterward. `HintsLimiter` maintains global per-PC attempt counts behind a mutex and prunes comparison entries beyond 10 attempts.

Dependencies and integration: uses traversal, sanitization, conditional checks, resource/type `uselessHint` filters, image compression, endian swap helpers, `specialInts`, and mutation execution callbacks from the fuzzer.

Risks: candidate volume can explode without limiter and cutoffs. Mutation order is partly map-derived but final replacers are sorted in `shrinkExpand`. Compressed-image mutation must carefully release decompressed buffers and restore original data. Skipping invalid conditional candidates avoids deep repairs but may miss useful hints.

Test signals: `hints_test.go` covers const/data/blob/compressed replacements, shrink/expand semantics, big-endian matching, call-level filtering, random validation, intersection, limiter accumulation, and benchmark behavior.
