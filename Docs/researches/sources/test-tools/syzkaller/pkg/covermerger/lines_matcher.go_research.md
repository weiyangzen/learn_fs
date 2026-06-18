# sources/test-tools/syzkaller/pkg/covermerger/lines_matcher.go

Purpose: builds a source-line-to-destination-line matcher between two versions of a file, preserving only lines whose text still matches at the mapped destination.

Important APIs/types/functions: `makeLineToLineMatcher`, `LineToLineMatcher`, and `SameLinePos`.

Control flow: the matcher computes a diff between `textFrom` and `textTo` with no timeout. It maps destination character offsets to destination line indexes, then iterates source lines, uses `DiffXIndex` to find the corresponding destination position, and records the destination line only if the destination line text equals the source line text; otherwise it records `-1`.

State and persistence: immutable in-memory `lineToLine` slice.

Dependencies and integration: uses `github.com/sergi/go-diff/diffmatchpatch`. Called by `FileLineCoverMerger` for every available commit version relative to the base file.

Risks: `SameLinePos` does not bounds-check the requested line index. Diff timeout is disabled, so very large files or pathological diffs can be expensive. Identical repeated lines may map ambiguously depending on diff behavior.

Test signals: `lines_matcher_test.go` covers unchanged, inserted, removed, and changed first-line scenarios.
