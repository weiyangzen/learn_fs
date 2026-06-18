# Research: sources/test-tools/syzkaller/pkg/report/report_test.go

Purpose: package-level regression tests for parsing, symbolization, guilty-file extraction, helper utilities, and fuzz seed invariants across all registered reporters and shared fixtures.

Important APIs/types/functions: `flagUpdate` enables fixture rewriting. `TestParse`, `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, and `checkReport` implement the report fixture contract. `TestGuiltyFile`, `TestRawGuiltyFile`, and `parseGuiltyTest` validate guilty-file extraction. `TestSymbolize` validates symbolization fixtures. `forEachFile` runs tests for each OS plus shared `all` fixtures. `readDir` selects numeric fixture files. Utility tests cover `replace`, `Fuzz`, `Truncate`, and `SplitReportBytes`.

Control flow: parse fixtures contain metadata headers, a blank line, raw log, and optional `REPORT:` expected extraction. Tests instantiate each non-Windows reporter, run OS-specific and shared fixtures, compare titles/alt titles/type/frame/corruption/suppression/panic/executor/report bytes, and verify output/start/end/skip invariants. When `-update` is used and no explicit offsets are asserted, expected headers can be regenerated from parser output.

State and persistence: normal runs are read-only. With `-update`, fixture files can be rewritten via `os.WriteFile`; this is deliberate test maintenance state. Race mode reduces fixture coverage to limit cost.

Dependencies and integration points: depends on all constructors in `ctors`, `mgrconfig`, `targets`, `crash`, `osutil`, `testutil`, and `testify/assert`. It is the main consumer of `testdata/*/report`, `guilty`, `guilty_raw`, and `symbolize` fixture trees.

Risks: exact fixture comparisons are useful but can make intentional normalization changes noisy. `forEachFile` runs shared `all` fixtures through every OS reporter, so generic runtime panic formats must stay compatible with all backends. The update path can accidentally bless regressions if used without review.

Test signals: failures identify crash-detection disagreement, empty titles, wrong metadata, bad report extraction, invalid offsets, guilty-file drift, symbolization drift, helper regressions, or fuzz seed panics.
