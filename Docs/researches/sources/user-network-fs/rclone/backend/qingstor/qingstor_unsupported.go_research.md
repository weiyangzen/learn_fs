# sources/user-network-fs/rclone/backend/qingstor/qingstor_unsupported.go

## Purpose
QingStor unsupported-platform shim: keeps package buildable on plan9/js.

## Important APIs, Types, And Functions
Important surface: package declaration under build tag.

## Control Flow
selected instead of real backend on unsupported targets

## State And Persistence
none.

## Dependencies And Integration Points
Go build constraints.

## Risks And Test Signals
Risks and useful test signals: backend unavailable on those targets by design.
