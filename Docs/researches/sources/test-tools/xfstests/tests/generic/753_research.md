# sources/test-tools/xfstests/tests/generic/753


Purpose: Exercises metadata-journal recovery under repeated simulated disk failures while fsstress emphasizes xattr creation, listing, and removal.


Important APIs, helpers, and commands: Imports `common/dmerror`; uses `_dmerror_init/mount/unmount/load_error_table/load_working_table`, `_run_fsstress_bg`, `_kill_fsstress`, `_require_metadata_journaling`, and soak loop helpers.
 Local helper functions detected in the file include `_cleanup`.
 It imports `./common/dmerror`, `./common/preamble`.
 Capability gates include `_require_dm_target`, `_require_metadata_journaling`, `_require_scratch`.



Control flow, state, dependencies, risks, and test signals: After mkfs and dm-error setup, the script builds fsstress weights biased toward xattrs, starts fsstress, randomly sleeps 0-2 seconds, flips the device to error without lockfs quiescing, kills fsstress, remounts through the working table for log replay, and repeats. State includes the dm-error mapping, scratch metadata log, fsstress process, and created xattrs. Dependencies are device-mapper error target and journaling filesystem. Risks include destructive error injection, unmount failures, and xattr workload variance. Success is repeated remount/recovery without check failures. Source size is 85 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
