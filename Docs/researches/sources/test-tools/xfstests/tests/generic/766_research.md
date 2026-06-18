# sources/test-tools/xfstests/tests/generic/766


Purpose: Tests readonly norecovery behavior with an external log device after filesystem shutdown, ensuring mounts with and without the external logdev fail/succeed as expected.


Important APIs, helpers, and commands: Uses `_require_logdev`, `_require_norecovery`, `_require_scratch_shutdown`, `_try_scratch_mount`, `_filter_ro_mount`, `_filter_ending_dot`, and scratch shutdown/unmount helpers.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/filter`, `./common/preamble`.
 Capability gates include `_require_local_device`, `_require_logdev`, `_require_metadata_journaling`, `_require_norecovery`, `_require_scratch_nocheck`, `_require_scratch_shutdown`.
 Regression annotations include `_fixed_by_fs_commit ext4 273108fa5015 \, _fixed_by_fs_commit xfs bfecc4091e07 \`.



Control flow, state, dependencies, risks, and test signals: The test formats scratch with log device, mounts, shuts the filesystem down, unmounts, then attempts readonly/norecovery mount variants using the proper and improper device configuration. State is the external log metadata and shutdown log state. Dependencies are local block devices, metadata journaling, and logdev support. Risks are mount option output variance and destructive shutdown. Signals are filtered mount success/failure lines matching expected behavior. Source size is 136 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
