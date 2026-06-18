# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.cs

## Purpose

Partial SMB1 file-store helper for create/delete/rename/check/query/set operations built on NT create and set-info primitives.

## Important APIs, Types, And Functions

Methods include `CreateDirectory`, `DeleteDirectory`, `DeleteFile`, `Delete`, `Rename`, `CheckDirectory`, `QueryInformation`, `SetInformation`, `SetInformation2`, and `GetFileAttributes`.

## Control Flow

Most helpers open a path with the required access/disposition/options, perform one metadata operation, then close. Delete sets `FileDispositionInformation.DeletePending`; rename sets `FileRenameInformationType2`; set-info builds `FileBasicInformation`.

## State And Persistence Behavior

Mutates persistent filesystem state for create, delete, rename, and attribute/time updates. Temporary handles are closed before return.

## Dependencies And Integration Points

Depends on `INTFileStore`, NT file information structures, access masks, create options/dispositions, and `SecurityContext`.

## Risks And Edge Cases

Delete and rename rely on delete access and share-delete semantics; conflicts surface as file-store statuses. `SetInformation` only maps hidden/read-only/archive and last-write time, omitting other SMB attributes. `CheckDirectory` opens with zero access, which may vary by backend.

## Test Signals

Test create existing, delete file versus directory, delete-on-close, rename directory/file cases, check-directory errors, query info close behavior, and attribute mapping.

Source-read signal: reviewed the complete local source file for this item.
