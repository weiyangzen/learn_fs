# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/CloseHelper.cs

## Purpose

Builds SMB1 close responses for file handles and find-search handles.

## Important APIs, Types, And Functions

`GetCloseResponse` closes a file-store handle for a request FID and removes it from the session. `GetFindClose2Response` removes an open search by search handle.

## Control Flow

File close validates FID, calls `CloseFile`, returns an error response on failure, logs success, removes the open file, and returns `CloseResponse`.

## State And Persistence Behavior

Mutates session open-file and open-search dictionaries; persistent file state is affected by file-store close semantics such as delete-on-close.

## Dependencies And Integration Points

Uses SMB1 close command types, `SMB1Session`, `OpenFileObject`, `ISMBShare.FileStore`, and logging.

## Risks And Edge Cases

Find close does not validate whether the search handle existed. File close assumes session lookup succeeds.

## Test Signals

Test valid close, invalid FID status, close failure propagation, delete-on-close effects in the file store, and find-close handle removal.

Source-read signal: reviewed the complete local source file for this item.
