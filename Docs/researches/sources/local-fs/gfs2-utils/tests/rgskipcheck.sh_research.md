# File Research: sources/local-fs/gfs2-utils/tests/rgskipcheck.sh

Shell checker for `rg_skip` chain consistency.

Behavior:
1. Gets resource group count from `gfs2_edit -p rgcount`.
2. Reads the first resource group address.
3. Iterates through all groups plus a final sentinel.
4. For each group, computes expected skip as current address minus previous address.
5. Verifies previous `rg_skip` equals the expected distance.
6. Requires the last `rg_skip` to be zero.

Research notes:
- Uses `gfs2_edit -p rg <i>` output and simple `grep`/`awk` parsing.
- Used by autotest wiring through `tests/Makefile.am`.
