# File Research: sources/windows/reactos/drivers/filesystems/npfs/secursup.c

## Purpose
Manages per-CCB client security contexts and impersonation support.

## Main Responsibilities
- `NpImpersonateClientContext` impersonates the stored client context or returns `STATUS_CANNOT_IMPERSONATE`.
- `NpFreeClientSecurityContext` dereferences the client token and frees the context allocation.
- `NpCopyClientContext` moves a data-queue-entry client context into the CCB.
- `NpUninitializeSecurity` frees and clears `Ccb->ClientContext`.
- `NpInitializeSecurity` stores client QoS:
  - Defaults to dynamic tracking, impersonation level, effective-only.
  - For dynamic tracking, does not capture a token immediately.
  - For static tracking, allocates and creates a client security context.
- `NpGetClientSecurityContext` captures a dynamic client context for client-end writes when required.

## Important Interactions
- Create path initializes security when a client connects.
- Write queue entries can carry client context for later server impersonation.
- Read path copies the writer context to the CCB when data is consumed.
- FSCTL impersonation uses the current CCB context.

## Risks / Review Notes
- Correct ownership transfer is subtle: queue entries may own a context until `NpCopyClientContext` moves it to the CCB.
- Dynamic tracking intentionally delays capture until write time for client-originated writes.
