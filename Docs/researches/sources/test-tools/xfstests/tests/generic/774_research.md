# sources/test-tools/xfstests/tests/generic/774


Purpose: fio atomic write stress for multi-fsblock atomic writes with unwritten/written block transitions and verification.


Important APIs, helpers, and commands: Uses fio config generation for write and verify jobs, `_require_scratch_write_atomic_multi_fsblock`, `_get_block_size`, `_require_fio_atomic_writes`, and xfs_io preparation.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_aio`, `_require_fio`, `_require_fio_atomic_writes`, `_require_odirect`, `_require_scratch_write_atomic_multi_fsblock`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The flow computes block and atomic unit sizes, prepares file regions with unwritten and written blocks, runs fio atomic write jobs at several sizes/increments, and verifies content. State is file extent state, fio configs, and verification output. Dependencies are fio AIO/direct atomic writes and multi-fsblock filesystem support. Risks are alignment, unwritten extent conversion bugs, and fio semantics. Signals are verify mismatches or fio errors. Source size is 128 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
