# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.QueryDirectory.cs

## Purpose

Partial SMB1 helper for directory enumeration by wildcard pattern.

## Important APIs, Types, And Functions

`QueryDirectory` splits a file-name pattern into directory path and search pattern, opens the directory, calls `fileStore.QueryDirectory`, closes the handle, and returns entries.

## Control Flow

The method requires at least one backslash separator. It opens the containing directory with list/traverse/synchronize access and synchronous directory options, then queries entries matching the final component.

## State And Persistence Behavior

No persistent mutation. Returned entries may later be cached in `OpenSearch` for SMB1 find-next.

## Dependencies And Integration Points

Uses `INTFileStore.CreateFile`, `QueryDirectory`, `FileInformationClass`, and `SecurityContext`.

## Risks And Edge Cases

Patterns without a slash return invalid parameter. Directory handles are temporary, so very large searches are materialized into a list before pagination. Access and sharing conflicts can stop enumeration.

## Test Signals

Test `\dir\*`, exact file, wildcard prefixes, malformed patterns, unsupported information classes through callers, and handle closure after query.

Source-read signal: reviewed the complete local source file for this item.
