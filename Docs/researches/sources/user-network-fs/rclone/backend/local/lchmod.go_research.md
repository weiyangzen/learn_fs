
# sources/user-network-fs/rclone/backend/local/lchmod.go

## Purpose
Defines a safe no-op `lChmod` implementation for platforms where changing symlink permissions without following the link is unavailable or unsafe.

## Important APIs, Types, And Control Flow
Sets `haveLChmod = false` and implements `lChmod(name, mode)` to return nil without modifying anything.

## State And Persistence
No filesystem state changes occur.

## Dependencies And Integration Points
Used by metadata writing when `--links` targets translated symlinks. Build tags cover Windows, Plan 9, JS, and Linux.

## Risks And Test Signals
The silent no-op avoids unsafe target chmod but means requested symlink mode metadata is not persisted. Tests should assert metadata writes do not alter symlink targets on these platforms.
