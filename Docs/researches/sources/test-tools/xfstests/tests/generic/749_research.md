# sources/test-tools/xfstests/tests/generic/749


Purpose: Validates mmap POSIX partial-page behavior: bytes beyond EOF up to page boundary read as zero, writes there do not change file size/content, and access beyond the mapped page boundary SIGBUSes.


Important APIs, helpers, and commands: Defines `filter_xfs_io_data_unique`, `setup_zeroed_file`, `mwrite`, `do_mmap_tests`, and `test_block_size`; uses `_mread`, `_round_up_to_page_boundary`, `_md5_checksum`, `truncate`, `falloc`, `mmap`, `mread`, and `mwrite` xfs_io commands.
 Local helper functions detected in the file include `do_mmap_tests`, `filter_xfs_io_data_unique`, `mwrite`, `setup_zeroed_file`, `test_block_size`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_scratch_nocheck`, `_require_test`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The test creates sparse or preallocated files, writes data at varied offsets/lengths, remounts to drop cache effects, verifies zero-filled tails, compares checksums and file sizes, and probes valid and invalid read/write ranges. State includes page-cache mappings, file size, checksums, and temp stderr/stdout used to detect `Bus error`. Dependencies are scratch filesystem, xfs_io mmap/truncate/falloc support, bash subprocess SIGBUS handling, and filter helpers. Risks are architecture page-size differences, shell signal text differences, and stale cache effects if cycle mounts fail. Test signals are explicit failure messages or final silence. Source size is 258 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
