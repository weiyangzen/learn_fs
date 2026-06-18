# sources/test-tools/xfstests/tests/generic/793


Purpose: Stresses zoned filesystem garbage collection by overwriting the same 1GiB file once per sequential-write-required zone.


Important APIs, helpers, and commands: Uses `_require_zoned_device`, `blkzone report`, `_require_no_compress`, `_scratch_mkfs_sized`, and `dd`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_command`, `_require_no_compress`, `_require_scratch_size`, `_require_zoned_device`.
 Regression annotations include `_fixed_by_fs_commit btrfs 7bcb04de982f \, _fixed_by_fs_commit btrfs 258e46a6385c \, _fixed_by_fs_commit btrfs e2a7fd22378f \`.



Control flow, state, dependencies, risks, and test signals: The test selects scratch realtime device if present, otherwise scratch device, verifies zoned support, formats a 16GiB scratch filesystem, counts `SEQ_WRITE_REQUIRED` zones, and overwrites `$SCRATCH_MNT/test` with 1GiB of zeros that many times. State is zone write pointers, filesystem data allocation, and GC/reclaim metadata. Dependencies are blkzone and a zoned block device. Risks are long runtime, device wear, and compression invalidating space assumptions. Signal is no dd failure and final silence. Source size is 53 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
