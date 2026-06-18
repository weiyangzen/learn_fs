
# sources/user-network-fs/rclone/backend/local/about_windows.go

## Purpose
Provides Windows local filesystem quota reporting.

## Important APIs, Types, And Control Flow
`About` converts `f.root` to UTF-16 and invokes `GetDiskFreeSpaceExW`, returning total bytes, total-free-derived used bytes, and user-available bytes as `fs.Usage`.

## State And Persistence
No filesystem state is modified; it only queries Kernel32.

## Dependencies And Integration Points
Uses `golang.org/x/sys/windows`, `unsafe`, and rclone `fs.Usage`. The backend implements `fs.Abouter` under the Windows build tag.

## Risks And Test Signals
Risks include path conversion failures and Windows API errno handling. Tests should check UNC/long-path roots and that available free space honors user quotas rather than raw volume free bytes.
