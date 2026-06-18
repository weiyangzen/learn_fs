
# sources/user-network-fs/rclone/backend/local/about_unix.go

## Purpose
Adds quota/usage reporting for local filesystems on Darwin, DragonFly, FreeBSD, and Linux.

## Important APIs, Types, And Control Flow
`About` calls `syscall.Statfs` on `f.root`, translates missing root into `fs.ErrorDirNotFound`, and returns `fs.Usage` using block size times total blocks, used blocks, and available blocks.

## State And Persistence
No persistent state is changed. It reads filesystem statistics from the kernel.

## Dependencies And Integration Points
Depends on `syscall.Statfs` and rclone `fs.Usage`. The compile-time interface assertion makes local `Fs` an `fs.Abouter` on supported Unix platforms.

## Risks And Test Signals
Risk is platform-specific interpretation of `Bfree` versus `Bavail`; available space is user-visible upload capacity. Tests should verify missing-root mapping and sane totals on temporary filesystems.
