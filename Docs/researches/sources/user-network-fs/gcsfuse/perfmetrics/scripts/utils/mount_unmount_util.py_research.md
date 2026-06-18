<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/mount_unmount_util.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/mount_unmount_util.py

## Purpose
Shared GCSFuse mount/unmount helpers for Python benchmarks.

## Important APIs, Types, And Functions
`mount_gcs_bucket(bucket_name, gcsfuse_flags, log)` creates a same-named directory and runs `gcsfuse`; `unmount_gcs_bucket(gcs_bucket, log)` runs lazy `umount -l` and removes the directory.

## Control Flow
`mount_gcs_bucket(bucket_name, gcsfuse_flags, log)` creates a same-named directory and runs `gcsfuse`; `unmount_gcs_bucket(gcs_bucket, log)` runs lazy `umount -l` and removes the directory.

## State And Persistence Behavior
Creates/removes local mount directories and mutates mounted filesystems.

## Dependencies
Uses Python stdlib and local benchmark conventions.

## Integration Points
Imported by rename and listing benchmarks.

## Risks And Edge Cases
Uses shell interpolation and drops into interactive `bash` on errors; return value is `None` on mount failure.

## Test Signals
Covered by the sibling test file when present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/mount_unmount_util.py -->
