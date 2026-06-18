# File Research: sources/windows/reactos/drivers/filesystems/fastfat/acchksup.c

## Purpose

`acchksup.c` implements access-check support for the ReactOS FastFAT driver. FAT has no per-file ACLs, so this file enforces FAT attribute-based restrictions and performs device/volume-level privilege checks through Windows security APIs.

## Main Responsibilities

- Reject user access to FAT volume-label and device directory entries.
- Validate requested file access masks against the subset FastFAT understands.
- Enforce read-only file restrictions while allowing directory-specific operations when appropriate.
- Check `SE_MANAGE_VOLUME_PRIVILEGE`.
- Determine whether a caller has explicit access to the underlying device object, excluding access obtained only through the Everyone SID.
- Build a restricted token with the Everyone SID disabled for deny-only use.

## Key Functions

`FatCheckFileAccess`

- Inputs: FAT dirent attributes and desired access mask.
- Denies access to `FAT_DIRENT_ATTR_VOLUME_ID` and `FAT_DIRENT_ATTR_DEVICE`.
- Rejects unknown access bits outside the allowed set.
- For read-only entries, blocks write-data/append-like access while still allowing metadata/security-style access such as `READ_CONTROL`, `WRITE_DAC`, `WRITE_OWNER`, `SYNCHRONIZE`, EA access, and attribute access.
- If the read-only object is a directory, it still allows add-file/add-subdirectory/delete-child style directory operations.
- Uses SEH-style cleanup only for tracing/unwind consistency; no complex resource cleanup occurs.

`FatCheckManageVolumeAccess`

- Constructs a one-privilege `PRIVILEGE_SET` containing `SE_MANAGE_VOLUME_PRIVILEGE`.
- Calls `SePrivilegeCheck` against the access state's subject security context.
- Returns boolean privilege possession.

`FatExplicitDeviceAccessGranted`

- Fast path succeeds if `PreviouslyGrantedAccess` includes any specific right except pure `FILE_TRAVERSE`.
- Also succeeds for callers with manage-volume privilege.
- Otherwise locks the subject context, finds the effective token manually, creates a restricted token with Everyone disabled, temporarily swaps that token into the subject context, and calls `SeAccessCheck` against the device object's security descriptor.
- Restores the original token, unlocks the subject context, dereferences the restricted token, and returns the status from `SeAccessCheck`.

`FatCreateRestrictEveryoneToken`

- Creates a restricted token using `SeFilterToken`.
- Disables `SeWorldSid` by placing it in a one-entry `TOKEN_GROUPS` list.
- The caller must dereference the returned token with `ObDereferenceObject`.

## Dependencies and Interactions

- Depends on `fatprocs.h` for driver-wide types, flags, tracing, and FAT attribute constants.
- Uses NT security manager APIs: `SePrivilegeCheck`, `SeLockSubjectContext`, `SeReleaseSubjectContext`, `SeAccessCheck`, `SeFilterToken`.
- Uses object manager cleanup via `ObDereferenceObject`.
- `IoGetFileObjectGenericMapping()` supplies the generic mapping for device security checks.

## Invariants and Safety Notes

- `FatExplicitDeviceAccessGranted` must always restore the original effective token after the restricted-token check.
- Subject context locking spans the temporary token substitution and access check.
- `FatCreateRestrictEveryoneToken` initializes `*RestrictedToken` to `NULL` before calling `SeFilterToken`.
- Access decisions are deliberately coarse because FAT stores attributes, not ACLs.

## Error and Edge Cases

- If restricted token creation fails, `FatExplicitDeviceAccessGranted` releases the subject context before returning the failure status.
- If access was granted only through Everyone, the restricted-token recheck should fail unless another explicit ACE grants access.
- Read-only handling is attribute-based, not ACL-based, so it cannot express richer security semantics.
