# sources/test-tools/xfstests/tests/generic/760


Purpose: Runs direct-I/O fsx using hugepage-backed buffers, aligning read/truncate/write sizes to page and device DIO limits.


Important APIs, helpers, and commands: Uses `_require_odirect`, `_require_thp`, `_require_hugepage_fsx`, `feature -s`, `min_dio_alignment`, and `_run_hugepage_fsx` with `-Z -R -W` direct options.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_hugepage_fsx`, `_require_odirect`, `_require_test`, `_require_thp`.



Control flow, state, dependencies, risks, and test signals: It computes system page size and DIO block size, then performs three direct hugepage fsx runs at different offsets. State is direct I/O test files and helper model state. Dependencies are O_DIRECT, THP, and correct min alignment. Risks are alignment mismatch and devices with strict DIO constraints. Success is no fsx corruption or I/O failure. Source size is 27 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
