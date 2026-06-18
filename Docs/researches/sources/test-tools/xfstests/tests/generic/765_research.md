# sources/test-tools/xfstests/tests/generic/765


Purpose: Broad atomic write support validator across filesystem block sizes, testing filesystem/device limits and data integrity for supported configurations.


Important APIs, helpers, and commands: Imports `common/atomicwrites`; defines `get_supported_bsize`, `get_mkfs_opts`, and `test_atomic_writes`; uses `_require_scratch_write_atomic`, `_require_atomic_write_test_commands`, atomic write unit sysfs/statx helpers, and `_test_atomic_file_writes`.
 Local helper functions detected in the file include `get_mkfs_opts`, `get_supported_bsize`, `test_atomic_writes`.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_atomic_write_test_commands`, `_require_scratch_write_atomic`.



Control flow, state, dependencies, risks, and test signals: The script determines min/max filesystem block sizes for XFS or ext4, formats scratch at candidate block sizes, mounts, obtains atomic write unit min/max and segment limits, and runs atomic file write helper coverage. State includes scratch format options, atomic-write capability values, and generated test files. Dependencies are kernel atomic write support, block device capability, xfs/ext4 mkfs options, and helper programs. Risks are filesystem-specific skip logic, device queue capability interpretation, and incomplete coverage if mount probes fail. Signals are helper failures or unsupported skips. Source size is 130 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
