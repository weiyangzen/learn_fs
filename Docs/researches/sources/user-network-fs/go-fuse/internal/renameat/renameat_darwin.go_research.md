# `sources/user-network-fs/go-fuse/internal/renameat/renameat_darwin.go`

## Purpose
Darwin renameat implementation using `renameatx_np`.

## Important APIs, Types, And Functions
Defines `SYS_RENAMEATX_NP`, `RENAME_SWAP`, `RENAME_EXCHANGE`, converts paths to C strings, and performs `Syscall6`.

## Control Flow
Defines `SYS_RENAMEATX_NP`, `RENAME_SWAP`, `RENAME_EXCHANGE`, converts paths to C strings, and performs `Syscall6`.

## State And Persistence
State is host filesystem namespace changes. Risk is syscall number/API compatibility across Darwin versions.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is host filesystem namespace changes. Risk is syscall number/API compatibility across Darwin versions.

## Test Signals
State is host filesystem namespace changes. Risk is syscall number/API compatibility across Darwin versions.
