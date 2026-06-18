# sources/test-tools/syzkaller/pkg/subsystem/extractor.go

## Purpose

`extractor.go` implements high-level subsystem inference from crash evidence. It combines path-based matches from guilty source paths and syscall-based matches from syzkaller reproducers, then applies voting and parent-pruning rules to return the most specific subsystem candidates.

## Important APIs, Types, and Functions

`Extractor` owns a `rawExtractorInterface`, allowing production use via `makeRawExtractor` and unit tests via mocks. `Crash` contains `GuiltyPath` and `SyzRepro`. Public entry points are `MakeExtractor`, `Extract`, and `TracedExtract`. Internal helpers include `readableSubsystems`, `mostVoted`, and `removeParents`.

## Control Flow

`TracedExtract` first collects all path-derived subsystems, logs each crash through `debugtracer.DebugTracer`, removes parent subsystems when children are present, and counts path votes by subsystem pointer. It then inspects reproducers. A subsystem that appears in every non-empty reproducer is treated as strong evidence. If such repro evidence is also the same as, or a child of, a path-derived subsystem, only the repro-derived child candidates are returned. With at least three reproducers, unrelated all-repro candidates may be combined with non-controversial stack candidates that clear a 66% vote share. Otherwise repro candidates add extra votes and final selection keeps subsystems at or above a 33% share, followed by parent removal.

## State, Dependencies, Risks, and Test Signals

Extractor state is read-only after construction except for the raw matcher internals. It does not persist data. Dependencies include `debugtracer`, `strings`, `math`, and the raw extractor's integration with path and syscall matching. Risks include pointer-identity vote keys, nondeterministic map iteration order, hard-coded thresholds, a typo in one trace message, and reliance on acyclic parent graphs. Tests in `extractor_test.go` cover parent shadowing, mixed repro signals, and repro-supported disambiguation.
