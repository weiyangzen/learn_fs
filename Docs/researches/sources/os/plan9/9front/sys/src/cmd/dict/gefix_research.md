# File Research: sources/os/plan9/9front/sys/src/cmd/dict/gefix

German-English raw index cleanup and canonicalization pipeline.

Key elements:
- Strips trailing whitespace and drops malformed non-tabbed lines.
- Removes pronunciation marker `\N'349'` and apostrophe-like quote markers.
- Normalizes leading/trailing hyphens around headword fields.
- Expands parenthesized variants and `(r, s)` suffix variants.
- Emits both `ß` and `ss` forms.
- Uses `awk` to emit `term<TAB>offset`, lowercases, and sorted-uniques the output.

Dependencies:
- Uses Plan 9 `rc`, `sed`, `awk`, `tr`, and `sort`.

Research notes:
- Encodes German-specific index normalization rules before feeding data to `dict`.
