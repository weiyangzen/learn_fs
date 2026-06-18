# File Research: sources/os/plan9/9front/sys/src/cmd/diff/merge3.c

Standalone three-way merge command built on the same `Diff` machinery as `diff`.

Key behavior:
- Usage is `merge3 theirs base ours`.
- It computes `base -> theirs` and `base -> ours` diffs with `calcdiff`.
- `collect` converts each diff’s match vector into sorted change ranges.
- `merge` walks both change streams, emits unchanged base ranges, applies non-overlapping changes, and handles overlapping edits.
- Overlapping edits are expanded to aligned old-file ranges, then `same` compares replacement text. Identical replacements are accepted once; differing replacements produce conflict markers.
- Conflict output uses `<<<<<<<<<<`, `========== original`, `========== <ours>`, and `>>>>>>>>>>`.
- Exits with status `"conflict"` on conflicts and rejects binary merges.

Notable dependencies:
- `calcdiff`, `fetch`, `readline`, and `freediff` from the diff implementation.

Research notes:
- The code mutates `Change` ranges while aligning overlaps, so collected changes are not immutable.
- `ln` tracks the next base line to emit; range printing uses existing `fetch` offset arrays.
- The file contains a Unicode identifier `δ`, unusual in otherwise old Plan 9 C style.
