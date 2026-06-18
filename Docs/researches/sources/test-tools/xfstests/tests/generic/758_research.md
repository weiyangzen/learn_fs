# sources/test-tools/xfstests/tests/generic/758


Purpose: Checks that mmap writes after `fzero` over a range spanning pages preserve the intended data before and after remount.


Important APIs, helpers, and commands: Uses xfs_io `pwrite`, `mmap`, `mwrite`, `fzero`, `_hexdump`, `_get_page_size`, `_scratch_cycle_mount`, and `_filter_xfs_io`.
 Local helper functions detected in the file include `_dump_files`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: It builds a verify file with baseline bytes and overwritten range, builds the test file through mmap write, zero-range, and mmap rewrite, compares the two files before remount, cycles mount, and compares again. State is file content, zeroed extents, page cache mappings, and post-remount disk state. Dependencies are scratch and xfs_io fzero/mmap support. Risks center on page-size/filesystem-block-size interactions and mmap cache coherency. Signals are cmp mismatches plus hexdumps. Source size is 68 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
