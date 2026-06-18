# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1Session.cs

## Purpose

Stores SMB1 authenticated session state, connected tree shares, open file handles, and open directory searches.

## Important APIs, Types, And Functions

Tree methods add, get, disconnect, and test TIDs. File methods add, get, remove, and report open files. Search methods allocate, add, get, and remove search handles. `Close` disconnects all trees.

## Control Flow

Adding a tree or file asks the connection for a globally unique TID/FID, then stores the share or `OpenFileObject`. Disconnecting a tree closes every open file under that tree through the share's file store before removing the tree.

## State And Persistence Behavior

Session-local in-memory dictionaries. Persistent file effects happen only through the underlying file store handles.

## Dependencies And Integration Points

Uses `ISMBShare`, `OpenFileObject`, `OpenSearch`, `SecurityContext`, and SMB1 connection id allocation.

## Risks And Edge Cases

Search dictionaries are mutated without the same connection lock used for files. The session key is stored but not exposed in this file, so signing use must be elsewhere. `MaxSearches` is declared but not enforced.

## Test Signals

Test tree disconnect closing only matching handles, FID uniqueness across sessions, search pagination handles, and `Close` cleanup with multiple shares.

Source-read signal: reviewed the complete local source file for this item.
