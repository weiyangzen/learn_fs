# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.QueryFileSystem.cs

## Purpose

Partial SMB1 helper for querying filesystem information and converting it to SMB1 transaction2 query levels.

## Important APIs, Types, And Functions

`GetFileSystemInformation` maps `QueryFSInformationLevel` to `FileSystemInformationClass`, calls `fileStore.GetFileSystemInformation`, converts through `QueryFSInformationHelper`, and returns an NT status.

## Control Flow

Unsupported SMB1 levels are caught and mapped to `STATUS_OS2_INVALID_LEVEL`; file-store failure statuses pass through.

## State And Persistence Behavior

Read-only filesystem metadata query.

## Dependencies And Integration Points

Depends on `INTFileStore`, `QueryFSInformationHelper`, and filesystem information classes.

## Risks And Edge Cases

Conversion may lose information compared with passthrough classes. The helper does not enforce share read permissions; callers must do that.

## Test Signals

Test each supported level, unsupported level status, file-store failure propagation, and conversion of volume/size/device/attribute fields.

Source-read signal: reviewed the complete local source file for this item.
