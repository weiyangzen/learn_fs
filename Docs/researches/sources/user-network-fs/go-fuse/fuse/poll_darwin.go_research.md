# `sources/user-network-fs/go-fuse/fuse/poll_darwin.go`

## Purpose
Darwin implementation of `pollHack` using a direct `SYS_POLL` wrapper.

## Important APIs, Types, And Functions
Defines `pollFd`, `sysPoll`, and `pollHack`; it opens the synthetic poll file, tolerates sandbox EPERM, and performs zero-timeout poll.

## Control Flow
Defines `pollFd`, `sysPoll`, and `pollHack`; it opens the synthetic poll file, tolerates sandbox EPERM, and performs zero-timeout poll.

## State And Persistence
State is just a temporary fd. Dependencies are `syscall`, `unsafe`, and path joining. Risk is Darwin syscall ABI/sandbox behavior; integration is via `WaitMount`.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is just a temporary fd. Dependencies are `syscall`, `unsafe`, and path joining. Risk is Darwin syscall ABI/sandbox behavior; integration is via `WaitMount`.

## Test Signals
State is just a temporary fd. Dependencies are `syscall`, `unsafe`, and path joining. Risk is Darwin syscall ABI/sandbox behavior; integration is via `WaitMount`.
