# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/comfix.awk

This AWK script expands comma-suffixed dictionary index entries into separate terms.

Key behaviors:
- Input records are expected as `offset<TAB>term`.
- If a term contains commas, the first comma-separated value is the base word.
- Later comma-separated suffixes are converted into derived words where possible.
- Single-letter suffixes replace the last base-word letter.
- Multi-letter suffixes search backward in the base word for a matching suffix start and accept approximate suffix-length matches.
- Unmatched suffixes are retained as `base, suffix`.

Notable implementation details:
- `matchsuflen()` implements the suffix-replacement heuristic and allows a length difference up to 3.
- Records not having exactly two fields are passed through unchanged.
