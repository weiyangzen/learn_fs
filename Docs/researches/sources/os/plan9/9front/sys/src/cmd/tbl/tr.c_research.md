# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tr.c

Allocates troff number-register names for table column measurements.

Key points:
- `nregs` is a fixed table of two-character register names.
- The comment notes it must contain at least `3*qcol` entries because each column needs left, middle, and right measurement registers.
- `reg(col, place)` bounds-checks against `qcol` and returns the register name for a given column and place.

Dependencies and interactions:
- Used throughout table rendering for column left/middle/right positions.
- Errors through `error` if too many columns are requested.

Research relevance:
- This is the central register-name mapping for `tbl` layout.
