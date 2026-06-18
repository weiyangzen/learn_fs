# sources/test-tools/xfstests/tests/generic/773


Purpose: fio-based atomic write verification for single-fsblock-capable filesystems using incremental, min/max, and verify jobs.


Important APIs, helpers, and commands: Defines `create_fio_aw_config`, `create_fio_verify_config`, and `create_fio_configs`; uses `_require_fio_atomic_writes`, `_require_aio`, O_DIRECT, xfs_io, and atomic unit helpers.
 It imports `./common/atomicwrites`, `./common/preamble`.
 Capability gates include `_require_aio`, `_require_fio`, `_require_fio_atomic_writes`, `_require_odirect`, `_require_scratch_write_atomic`, `_require_xfs_io_command`.



Control flow, state, dependencies, risks, and test signals: The test creates fio configs for atomic write workloads and verify passes, records min/max units, formats/mounts scratch, runs direct atomic write sequences, and verifies the written pattern. State includes fio state files/configs and scratch data. Dependencies are fio atomic write support and filesystem atomic write capability. Risks are fio version differences, direct-I/O alignment, and runtime scaling. Signals are fio or verify failures. Source size is 108 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
