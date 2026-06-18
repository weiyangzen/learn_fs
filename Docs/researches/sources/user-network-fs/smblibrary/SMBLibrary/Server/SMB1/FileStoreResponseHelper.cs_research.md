# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/FileStoreResponseHelper.cs

## Purpose

Implements SMB1 simple file-store command responses for create/delete directory, delete, rename, check directory, query/set file info, set info by FID, and disk information.

## Important APIs, Types, And Functions

Each `Get*Response` method validates access where the share is `FileSystemShare`, delegates to `SMB1FileStoreHelper` or `FileStore`, maps results into SMB1 response structures, logs, and returns `ErrorResponse` on failure.

## Control Flow

Path operations normalize or pass path strings, run share-level read/write checks, call helper methods, set `header.Status`, and build command-specific responses. Disk information queries `FileFsSizeInformation` and clamps counts to 16-bit SMB1 fields.

## State And Persistence Behavior

Mutates persistent filesystem through file-store operations for create, delete, rename, and set info. It also reads open-file state for SetInformation2.

## Dependencies And Integration Points

Depends on SMB1 command classes, `SMB1FileStoreHelper`, `FileSystemShare`, `INTFileStore`, and session security context.

## Risks And Edge Cases

Access checks are only applied for `FileSystemShare`, so named pipe or custom shares must enforce their own checks. Size fields are truncated for legacy responses. Several methods assume valid sessions.

## Test Signals

Cover access denied paths, file versus directory delete, rename source and target permissions, query/set info mapping, disk-size truncation, and invalid FID for SetInformation2.

Source-read signal: reviewed the complete local source file for this item.
