# File Research: sources/windows/dokany/sys/security.c

Implements security descriptor query and set dispatch/completion for files.

Key entry points:
- `DokanDispatchQuerySecurity()` validates file context, builds a `SECURITY_CONTEXT`, optionally creates an MDL for the caller's security output buffer, and registers the request.
- `DokanCompleteQuerySecurity()` validates returned relative security descriptors, copies them to the caller buffer, reports overflow sizes, updates context, and frees allocated MDLs.
- `DokanDispatchSetSecurity()` packages a self-relative security descriptor into `SET_SECURITY_CONTEXT` with aligned buffer offset and registers the request.
- `DokanCompleteSetSecurity()` updates context, reports security change notifications on success, and completes with user-mode status.

Core mechanics:
- Query logs requested owner/group/DACL/SACL/label security information flags.
- Query uses the original requested security buffer length and an MDL when `UserBuffer` is present.
- Returned descriptors are accepted only if `RtlValidRelativeSecurityDescriptor()` validates them for the requested security information.
- Buffer overflow is reported with `IoStatus.Information` set to the needed returned length.
- Set assumes the incoming descriptor is self-relative and uses `RtlLengthSecurityDescriptor()` for payload size.
- Set aligns the security descriptor buffer offset to a 4-byte boundary for Win32 compatibility.
- Oversized set-security events beyond `EVENT_CONTEXT_MAX_SIZE` are rejected.

Filesystem relevance:
- This file bridges Windows security descriptor operations to user-mode filesystems while preserving descriptor validation and change notification behavior.

Notable risks:
- Set-security currently has no large-buffer fallback path; oversized descriptors fail.
- Query completion only copies through an MDL-mapped buffer, so buffer setup must be correct.
- Security descriptor validity is checked on query replies, but set payload validity is mostly assumed from the incoming kernel parameter.
