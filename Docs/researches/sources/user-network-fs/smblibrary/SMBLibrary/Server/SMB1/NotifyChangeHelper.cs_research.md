# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NotifyChangeHelper.cs

## Purpose

Starts and completes asynchronous SMB1 NT transaction notify-change requests.

## Important APIs, Types, And Functions

`ProcessNTTransactNotifyChangeRequest` creates async context and calls `FileStore.NotifyChange`. `OnNotifyChangeCompleted` removes context, logs, builds an SMB1 NT transact response or error, and enqueues it.

## Control Flow

The start path locks the context to order logs, sets request status to pending or not implemented. Completion reacquires that lock, removes the async context, reconstructs an SMB1 header from saved ids, fragments success data through `NTTransactHelper`, or sends an error status.

## State And Persistence Behavior

Maintains pending async context in connection state and depends on file-store watch state until completion/cancel.

## Dependencies And Integration Points

Uses `SMB1AsyncContext`, `NTTransactNotifyChange*` structures, `SMBServer.EnqueueMessage`, and file-store `NotifyChange`.

## Risks And Edge Cases

The start method does not validate `openFile` before using `openFile.Handle`; invalid FID can throw. Completion silently drops output if the session disappeared. Oversized change lists are converted to `STATUS_NOTIFY_ENUM_DIR`.

## Test Signals

Test valid notify pending/completion, invalid FID, unsupported file store status mapping, oversized completion data, cancel completion, and session close before callback.

Source-read signal: reviewed the complete local source file for this item.
