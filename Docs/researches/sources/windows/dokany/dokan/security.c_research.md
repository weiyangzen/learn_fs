# File Research: sources/windows/dokany/dokan/security.c

Implements security descriptor query/set dispatch and a default security descriptor provider.

Key behavior:
- `DefaultGetFileSecurity`:
  - obtains current process user and first group SID;
  - builds SDDL owner/group text;
  - grants authenticated users full access, with directory inheritance flags for directories;
  - converts requested security information to a binary security descriptor;
  - returns `STATUS_BUFFER_OVERFLOW` with required length if the output buffer is too small.
- `DispatchQuerySecurity`:
  - calls filesystem `GetFileSecurity` if available;
  - falls back to `DefaultGetFileSecurity` on `STATUS_NOT_IMPLEMENTED`;
  - sets output buffer length on success or overflow.
- `DispatchSetSecurity`:
  - obtains the descriptor from an offset inside `EventContext`;
  - calls filesystem `SetFileSecurity` if available;
  - maps any non-success to `STATUS_INVALID_PARAMETER`.

Risks and notes:
- Some error paths in `DefaultGetFileSecurity` return before freeing all allocated SDDL strings/descriptors.
- Default ACL behavior is permissive toward authenticated users and intended as a fallback for UI/context-menu compatibility.
