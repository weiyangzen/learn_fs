# sources/test-tools/syzkaller/prog/hints_test.go

Purpose: validates comparison-guided hint mutation behavior across constants, data blobs, compressed images, complete calls, random programs, map intersection, and limiter state.

Important APIs/types/functions: `ConstArgTest`, `DataArgTest`, `TestHintsCheckConstArg`, `TestHintsCheckDataArg`, `TestHintsCompressedImage`, `TestHintsShrinkExpand`, `TestHintsCall`, `TestHintsRandom`, `extractValues`, `TestHintsData`, `TestInplaceIntersect`, `BenchmarkHints`, `TestHintsLimiter`, `perPCCount`, and `compSet`.

Control flow and state: table tests build synthetic `CompMap` values and assert exact replacements. Random tests generate programs, extract scalar/blob values, build comparison maps, and run `MutateWithHints` for validation. Limiter tests apply two rounds to prove per-PC counts accumulate and prune later maps.

Dependencies and integration: uses `image.Compress/MustDecompress`, target test descriptions, `Deserialize`, `Serialize`, `ForeachArg`, `newRand`, benchmarks, and `testify`.

Risks: exact expected mutations depend on `specialInts`, endian swap behavior, and sorted replacer order. Random tests skip oversized programs/calls to bound quadratic validation cost.

Test signals: very strong coverage of shrink/extend edge cases, bit sizes, negative values, special-int filtering, big-endian replacement, compressed image alignment, call-specific useless-hint filtering, and limiter pruning.
