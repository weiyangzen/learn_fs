<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/logger/log.go -->
# sources/sync-backup/restic/internal/backend/logger/log.go

## Purpose
Provides a backend decorator that logs calls and forwards them to the wrapped backend.

## Important APIs, Types, And Functions
Backend, New, IsNotExist, Save, Remove, Load, Stat, List, Delete, Close, and Unwrap are relevant.

## Control Flow
Each method logs the operation through debug.Log and delegates to the embedded backend. Load logs the request and passes through the consumer callback.

## State And Persistence Behavior
No state beyond wrapped backend pointer. Persistence is entirely delegated.

## Dependencies And Integration Points
Depends on context, io, internal/backend, and internal/debug.

## Risks And Edge Cases
Logging must avoid altering behavior; Unwrap allows later layers to recover the original backend.

## Test Signals
Covered indirectly by backend wrapper usage; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/logger/log.go -->
