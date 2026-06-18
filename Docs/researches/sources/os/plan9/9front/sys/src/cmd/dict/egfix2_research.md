# File Research: sources/os/plan9/9front/sys/src/cmd/dict/egfix2

Secondary English-German index transformer.

Key elements:
- Uses `awk` with tab/comma-space field splitting.
- Emits `term<TAB>offset` pairs by reversing fields after the first.
- Lowercases ASCII with `tr A-Z a-z`.
- Sorts uniquely using tab as delimiter and folded first field plus numeric offset.

Dependencies:
- Uses Plan 9 `rc`, `awk`, `tr`, and `sort`.

Research notes:
- Complements `egfix` by converting cleaned offset-to-term lines into canonical index order.
