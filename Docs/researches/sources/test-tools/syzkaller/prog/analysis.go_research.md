# sources/test-tools/syzkaller/prog/analysis.go

Purpose: implements conservative program analysis, argument traversal, feature detection, fallback coverage signal construction, compressed-asset enumeration, and a top-level `ContainsAny` query.

Important APIs/types/functions: `state` tracks target, choice table, corpus, observed filenames/strings/resources, and memory/VMA allocators. `analyze`, `newState`, `(*state).analyze`, and `analyzeImpl` walk calls and update allocation/resource/string/file state. `ArgCtx`, `ForeachArg`, `ForeachSubArg`, and `foreachArgImpl` are central traversal APIs used across checksum, encoding, hints, minimization, and conditional-field logic. `RequiredFeatures`, `CallInfo`, `FallbackSignal`, `DecodeFallbackSignal`, `ForEachAsset`, and `ContainsAny` are package-level program introspection entry points.

Control flow and state: `analyze` processes calls before a requested stop call with resource recording disabled once the stop call is reached. `analyzeImpl` records pointer heap/VMA allocations, output resources, non-output string buffers, and local non-escaping filenames. Traversal preserves and restores `ArgCtx` around recursive descent, carrying parent slices, field metadata, base pointer, offset, and optional parent stack. `FallbackSignal` walks executed calls, emits errno/blocked signals, collects successful resource producers, and adds constructor/argument-flag signals until a syscall with `BreaksReturns`.

Dependencies and integration: depends on `pkg/image` for decompressing `BufferCompressed` data and on `any.go` through `Target.CallContainsAny`. The traversal primitives are integration points for most other files in this subset. Fallback signal values must remain compatible with signal consumers and the `fallbackCallMask` bit layout.

Risks: traversal offset handling is subtle for overlays, varlen groups, unions, and pointer bases. `FallbackSignal` intentionally truncates errno space and call IDs; call ID overflow panics. `ForEachAsset` uses `image.MustDecompress`, so malformed compressed data would fail hard if earlier deserialization validation missed it.

Test signals: coverage is indirect through serialization, checksum, hints, minimization, images, and conditional-field tests. `images_test.go` directly verifies `ForEachAsset`; `prog_test.go` outside this item covers fallback signal behavior.
