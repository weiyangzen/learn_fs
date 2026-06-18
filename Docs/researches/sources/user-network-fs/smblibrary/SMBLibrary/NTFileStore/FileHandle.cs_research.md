<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/FileHandle.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/FileHandle.cs

## Purpose
`FileHandle` is a simple server-side handle container tying a logical path to a stream, directory flag, and delete-on-close behavior.

## Important APIs, Types, And Functions
Direct types: FileHandle class. Fields include Path:string, IsDirectory:bool, Stream:Stream, DeleteOnClose:bool.

## Control Flow
Construction stores the supplied path, directory bit, stream, and delete-on-close flag. Other file-store code uses the object as opaque handle state.

## State And Persistence Behavior
State is per-open-handle and persists only as long as the server keeps the handle object. It may own an open `Stream` that must be closed elsewhere.

## Dependencies And Integration Points
Integrated by NT file-store implementations that expose local or virtual files through SMB server operations.

## Risks
Risk centers on lifecycle ownership: streams must be closed exactly once and delete-on-close must be honored after all access checks and sharing rules.

## Test Signals
Test create/open/close flows, directory vs file handles, stream disposal, and delete-on-close cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/FileHandle.cs -->
