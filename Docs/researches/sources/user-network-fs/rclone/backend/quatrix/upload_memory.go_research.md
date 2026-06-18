# sources/user-network-fs/rclone/backend/quatrix/upload_memory.go

## Purpose
Quatrix upload memory manager: chooses dynamic chunk sizes from transfer speed and configured shared memory budget.

## Important APIs, Types, And Functions
Important surface: UploadMemoryManager, NewUploadMemoryManager, Consume, Return.

## Control Flow
static mode caps at minimal chunk; dynamic mode returns previous borrow, estimates speed*time chunk, borrows from shared pool, and records per-file borrow

## State And Persistence
in-memory mutex-protected shared pool and fileUsage map.

## Dependencies And Integration Points
rclone ConfigInfo and Quatrix Options.

## Risks And Test Signals
Risks and useful test signals: Return must be called on all paths, file ID reuse, zero speed minimal chunks, concurrent accounting.
