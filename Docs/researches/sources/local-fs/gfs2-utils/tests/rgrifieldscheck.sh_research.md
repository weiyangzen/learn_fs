# File Research: sources/local-fs/gfs2-utils/tests/rgrifieldscheck.sh

Shell consistency checker comparing rindex fields against resource group header fields via `gfs2_edit`.

Behavior:
1. Verifies `gfs2_edit -p rg 0` exposes `rg_data0`; exits success if fields are unavailable in old headers.
2. Iterates `gfs2_edit -p rindex`.
3. For `ri_data0`, `ri_data`, and `ri_bitbytes`, maps `ri*` to `rg*`.
4. Reads matching resource group field and compares values.
5. Fails with a diagnostic on mismatch.

Research notes:
- Increments resource group index when `ri_bitbytes` is processed.
- Used as a test script in `tests/Makefile.am`.
