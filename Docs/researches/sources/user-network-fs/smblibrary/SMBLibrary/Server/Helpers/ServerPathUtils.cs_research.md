# sources/user-network-fs/smblibrary/SMBLibrary/Server/Helpers/ServerPathUtils.cs

## Purpose

Provides helpers for extracting server-relative path, share-relative path, and share name from UNC-like server paths.

## Important APIs, Types, And Functions

`GetRelativeServerPath`, `GetRelativeSharePath`, and `GetShareName` operate on string paths such as `\\server\share\file`.

## Control Flow

The server-relative helper strips the leading server component. Share-relative helper strips the share component. Share-name helper strips leading slash then truncates at the next slash.

## State And Persistence Behavior

Stateless string utility.

## Dependencies And Integration Points

Used by server dispatch and tree-connect style path handling.

## Risks And Edge Cases

`GetRelativeSharePath` computes the separator index in `relativePath` but returns `path.Substring(index)`, which is wrong for UNC inputs because the index applies to the shortened string. It can return a substring from the original server name rather than the share-relative suffix.

## Test Signals

Test UNC server-only, UNC share-only, UNC share plus file, already-relative paths, no leading slash, and malformed empty strings.

Source-read signal: reviewed the complete local source file for this item.
