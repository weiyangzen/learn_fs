<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_access_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_access_test.go

## Purpose

This suite verifies that gcsfuse can mount a bucket using a service account that has only minimal list permission on the bucket, validating the mount-time permission requirement.

## Important APIs, Types, and Functions

`MountAccessTest` mirrors the mount-timeout binary harness with `gcsfusePath` and temp `dir`. `mountWithKeyFile` mounts with `--key-file`, trace log, and configured log file, then unmounts via `unmountAndWait`. `TestMountingWithMinimalAccessSucceeds` creates credentials and applies a custom role.

## Control Flow

The test checks bucket access with the default storage client, creates a temporary service account/key, grants custom role `storage.objects.list` on the bucket, mounts using the key file, unmounts, then revokes the role and removes the key. `TestMountAccess` sets a log file and runs the suite.

## State and Persistence Behavior

State includes temporary credentials, an IAM binding for the custom role, a temp mount directory, and logs saved as artifacts on mount failure. No object data is intentionally created.

## Dependencies and Integration Points

It depends on credentials helpers, custom-role IAM helpers, the gcsfuse binary built by package setup, and the shared `unmountAndWait` helper from `gcsfuse_mount_timeout_test.go`.

## Risks and Test Signals

IAM propagation and custom role existence are external prerequisites. The test only checks mount success, not later file operations. Passing signal is mount/unmount success with list-only credentials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_access_test.go -->
