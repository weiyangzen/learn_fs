# sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive_unsupported.go

## Purpose
Provides a buildable package stub for unsupported Plan9 and Solaris platforms so the Go package does not fail with "no buildable Go source files."

## Important APIs, Types, and Functions
The file declares package `iclouddrive` only. It exports no functions, types, variables, or interface implementations.

## Control Flow
The file is selected only by `//go:build plan9 || solaris`. Runtime behavior is intentionally absent.

## State and Persistence
No state is maintained.

## Dependencies and Integration Points
It integrates only with Go's build constraint system. The real Drive and Photos implementations are excluded on these platforms.

## Risks and Edge Cases
Any consumer expecting iCloud Drive symbols on Plan9/Solaris will not have them. This is deliberate but means platform support is compile-placeholder only.

## Test Signals
No tests target this stub directly. Its value is compile-time package availability on unsupported platforms.
