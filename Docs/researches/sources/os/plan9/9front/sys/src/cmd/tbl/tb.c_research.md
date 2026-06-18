# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tb.c

Provides cell-use analysis and simple arena-style storage for `tbl`.

Key points:
- `checkuse` scans all real table rows and marks per-column usage arrays: `used`, `lused`, and `rused`.
- Numeric/alphabetic split columns are tracked separately so zero-width left or right fields can be skipped during output.
- `real` distinguishes absent/empty cells from actual text or encoded non-pointer sentinel values.
- `chspace` allocates reusable character arenas of `MAXCHS + MAXLINLEN`, limited by `MAXVEC`.
- `alocv` allocates zeroed vector storage from reusable `MAXCHS` chunks, with `tpcount` and `thisvec` acting as a bump allocator.
- `release` resets allocation cursors and `exstore`; it intentionally does not free the underlying arenas.

Dependencies and interactions:
- Uses global column/row state from `t.h`.
- Allocation failures and excessive storage requests terminate through `error`.

Research relevance:
- This is support infrastructure for `tbl` layout decisions and memory reuse across tables.
