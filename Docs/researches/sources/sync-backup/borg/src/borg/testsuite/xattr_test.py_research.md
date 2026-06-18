# sources/sync-backup/borg/src/borg/testsuite/xattr_test.py

## Purpose
Tests Borg extended attribute wrappers for filesystem enablement, get/set/list behavior, buffer growth, length-prefixed string splitting, symlink behavior, and fakeroot flag detection.

## Important APIs, Types, and Functions
Uses `is_enabled`, `getxattr`, `setxattr`, `listxattr`, `XATTR_FAKEROOT`, `platform.xattr.buffer`, `split_lstring`, and `is_linux`. Helper `assert_equal_se` ignores common system attributes.

## Control Flow
The fixture creates a temp file and symlink only if xattrs are available. Tests set multiple user attributes on file paths and fds, optionally symlink attrs on non-Linux, force small platform buffers, and verify buffer resizing during list/get operations.

## State and Persistence Behavior
State lives in filesystem xattrs on temporary files/symlinks and in the platform xattr buffer singleton. Empty xattr values are distinct and must round trip as `b""`.

## Dependencies and Integration Points
Integrates Borg's portable xattr layer with platform-specific wrappers, Linux symlink restrictions, SELinux/macOS provenance filtering, and fakeroot environment detection.

## Risks and Test Signals
Risks include buffer truncation, platform-specific symlink errors, false fakeroot detection, and races with system-added xattrs. Signals are exact xattr lists/values after filtering, buffer length growth, `split_lstring` results, and `XATTR_FAKEROOT` false conditions.
