# File Research: sources/windows/windows-driver-samples/filesys/fastfat/acchksup.c

## Purpose

Provides FastFAT access-check support for FAT directory attributes, manage-volume privilege checks, explicit device ACL checks, and construction of a token that disables the Everyone SID.

## Key routines

- `FatCheckFileAccess`: filters requested file access against FAT dirent attributes.
- `FatCheckManageVolumeAccess`: checks whether the subject has `SE_MANAGE_VOLUME_PRIVILEGE`.
- `FatExplicitDeviceAccessGranted`: determines whether access was explicitly granted to the device object rather than only via Everyone.
- `FatCreateRestrictEveryoneToken`: creates a restricted token where `SeWorldSid` is disabled / deny-only.

## Access semantics

`FatCheckFileAccess` rejects volume ID and device dirents outright. It also rejects desired access masks containing rights outside the supported FAT set. For read-only dirents, it permits metadata/security-style access plus read-oriented access. For read-only directories, it additionally permits directory add and delete-child rights, matching FAT directory semantics.

`FatCheckManageVolumeAccess` builds a one-entry `PRIVILEGE_SET` for `SE_MANAGE_VOLUME_PRIVILEGE` and calls `SePrivilegeCheck`.

`FatExplicitDeviceAccessGranted` first accepts cases where specific access beyond traverse was already granted, and also accepts manage-volume privilege. Otherwise, it locks the subject context, selects the effective token, creates a restricted token without Everyone access, temporarily swaps that token into the subject context, and reruns `SeAccessCheck` against the device security descriptor. It restores the original token and dereferences the restricted token before returning.

## Dependencies

Uses FAT support declarations from `FatProcs.h`, FAT dirent attribute constants, Windows security token APIs (`SePrivilegeCheck`, `SeFilterToken`, `SeAccessCheck`, `SeLockSubjectContext`, `SeUnlockSubjectContext`), and object dereference APIs.

## Edge cases and notes

- The explicit-device check intentionally strips Everyone to distinguish broad public access from user/group-specific grants.
- `FatCreateRestrictEveryoneToken` returns a referenced token object that callers must release with `ObDereferenceObject`.
- `IrpContext` is unused in some routines except for interface consistency and tracing.
