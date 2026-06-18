# File Research: sources/virtualization/virtiofsd/src/passthrough/credentials.rs

## Scope

RAII helpers for temporarily applying guest credentials and temporarily dropping effective capabilities during passthrough filesystem operations.

## APIs Covered

- `UnixCredentials` stores target host UID, GID, supplementary groups, and whether to keep a capability workaround.
- `UnixCredentialsGuard` restores credentials and supplementary groups on drop.
- `ScopedCaps` drops one effective capability on creation and restores it on drop.
- `drop_effective_cap()` public helper.

## Behavior

- `UnixCredentials::set()` changes supplementary groups first, then effective GID, then effective UID.
- Root UID/GID targets are not changed, preserving legacy behavior.
- If supplementary-group extension is not available, it can temporarily add `DAC_OVERRIDE` after UID switch as a kernel compatibility workaround.
- Guard drop restores UID, GID, and drops supplementary groups, logging failures.
- `ScopedCaps` uses capng to drop an effective capability and later restore it; restore failures panic.

## Risks

Credential switching is per-thread by direct syscall wrappers. Ordering is important: changing UID before GID could lose privilege to change GID.
