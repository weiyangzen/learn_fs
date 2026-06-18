# File Research: sources/windows/reactos/drivers/filesystems/udfs/secursup.cpp

## Purpose

`secursup.cpp` implements UDFS security-descriptor support: IRP dispatch handlers for query/set security, ACL assignment/inheritance, security descriptor persistence in UDF named streams, and access/share checks used during open/create.

Most dispatch code is gated by `UDF_ENABLE_SECURITY`; write paths are further gated by `!UDF_READ_ONLY_BUILD`.

## Main Runtime Paths

- `UDFGetSecurity()` is the `IRP_MJ_QUERY_SECURITY` entry point. It enters the filesystem, establishes top-level IRP state, allocates a UDF IRP context, calls `UDFCommonGetSecurity()`, and routes exceptions through the UDF exception filter/handler.
- `UDFCommonGetSecurity()`:
  - extracts `FileObject`, `CCB`, `FCB`, and `NTRequiredFCB`
  - acquires the FCB main resource exclusively
  - obtains the caller buffer and requested query length
  - lazily assigns an ACL with `UDFAssignAcl()` if none is cached
  - calls `SeQuerySecurityDescriptorInfo()` into the caller buffer
  - completes or posts the IRP depending on acquisition/posting state
- `UDFSetSecurity()` and `UDFCommonSetSecurity()` mirror the dispatch structure for `IRP_MJ_SET_SECURITY`.
  - `UDFCommonSetSecurity()` rejects when `Vcb->WriteSecurity` is false.
  - It derives a `DesiredAccess` mask from security-information bits, but the computed mask is not subsequently used in this function.
  - It converts the cached descriptor to self-relative form, calls `SeSetSecurityDescriptorInfo()`, marks `UDF_NTREQ_FCB_SD_MODIFIED`, and sends a `FILE_NOTIFY_CHANGE_SECURITY` notification on success.

## ACL Persistence

- `UDFReadSecurity()` loads a security descriptor from the file’s stream directory:
  - opens the stream directory with `UDFOpenStreamDir__`
  - opens the named ACL stream `UDFGlobalData.AclName`
  - allocates a nonpaged buffer sized to the ACL stream
  - reads the stream and validates it with `RtlValidSecurityDescriptor`
  - maps missing stream directory or ACL stream to `STATUS_NO_SECURITY_ON_OBJECT`
- `UDFWriteSecurity()` writes modified descriptors back:
  - returns success without doing work when security writes are disabled, media is read-only, or the descriptor is not marked modified
  - creates the stream directory and ACL stream if needed
  - unlinks the ACL stream when the descriptor pointer is null
  - writes `RtlLengthSecurityDescriptor()` bytes and clears `UDF_NTREQ_FCB_SD_MODIFIED`

## Descriptor Construction And Ownership

- `UDFConvertToSelfRelative()` clones a descriptor through `SeQuerySecurityDescriptorInfo(FULL_SECURITY_INFORMATION)` into a nonpaged self-relative buffer.
- `UDFInheritAcl()` copies a parent descriptor with the same query API.
- `UDFBuildEmptyAcl()` allocates and initializes a bare security descriptor.
- `UDFBuildFullControlAcl()` creates a world-owned/world-group descriptor with a DACL granting `FILE_ALL_ACCESS` to `SeWorldSid`, then converts it to self-relative form.
- `UDFAssignAcl()` lazily attaches a descriptor to an FCB:
  - stream directories and streams reuse the parent file’s common FCB descriptor
  - volume security inherits from root when possible
  - ordinary files first try persisted ACL stream data, then inherit from parent, or build a full-control ACL for the root
- `UDFDeassignAcl()` either drops auto-inherited pointers without freeing or calls `SeDeassignSecurity()` for owned descriptors.

## Access Enforcement

- `UDFLookUpAcl()` ensures an ACL is assigned and returns `Fcb->NTRequiredFCB->SecurityDesc`.
- `UDFCheckAccessRights()` combines:
  - UDF read-only/media/integrity compatibility checks
  - optional `SeAccessCheck()` against the cached descriptor
  - `ACCESS_SYSTEM_SECURITY` privilege checking through `SeSinglePrivilegeCheck()`
  - Windows share-access checks via `IoCheckShareAccess()` / `IoSetShareAccess()`
- `UDFSetAccessRights()` wraps create/open-time security assignment:
  - without `UDF_ENABLE_SECURITY`, it delegates directly to `UDFCheckAccessRights()`
  - with security enabled, it uses `SeAssignSecurity()` against the parent descriptor and caller `ACCESS_STATE`, converts to self-relative form, then verifies access/share compatibility

## Integration

This file is tightly coupled to:

- FCB/CCB/VCB structures from `struct.h`
- stream-directory/file helpers such as `UDFOpenStreamDir__`, `UDFOpenFile__`, `UDFCreateFile__`, `UDFReadFile__`, `UDFWriteFile__`, and `UDFUnlinkFile__`
- UDF notification, delayed persistence, and descriptor modification flags
- Windows security manager APIs (`SeQuerySecurityDescriptorInfo`, `SeSetSecurityDescriptorInfo`, `SeAssignSecurity`, `SeAccessCheck`)

## Notable Risks

- Security is compile-time optional, so callers must tolerate `STATUS_NO_SECURITY_ON_OBJECT` or no-op persistence depending on build flags.
- Stream/stream-directory descriptors are pointer aliases to parent descriptors; `UDFDeassignAcl(..., AutoInherited=TRUE)` intentionally avoids freeing those aliases.
- `UDFCommonSetSecurity()` computes `DesiredAccess` but does not use it locally; authorization appears to be expected earlier in open/create paths.
- `UDFCheckAccessRights()` treats `Ccb` as optional in the signature, but the `ACCESS_SYSTEM_SECURITY` branch writes through `Ccb` without a local null guard.
