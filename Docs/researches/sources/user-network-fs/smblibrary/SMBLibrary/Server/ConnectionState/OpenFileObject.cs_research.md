# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/OpenFileObject.cs

## Purpose

Stores one open server-side file object in a session: tree id, share name, relative path, backing file-store handle, access mode, and open timestamp.

## Important APIs, Types, And Functions

Constructor records all fields. Properties expose `TreeID`, `ShareName`, mutable `Path`, `Handle`, `FileAccess`, and `OpenedDT`.

## Control Flow

No algorithmic flow; session dictionaries create, look up, mutate path on rename if needed, and remove instances.

## State And Persistence Behavior

This is in-memory open-file state. The actual persistent file state remains in the backing `INTFileStore` handle.

## Dependencies And Integration Points

Uses `System.IO.FileAccess`; consumed by SMB1/SMB2 sessions and command helpers.

## Risks And Edge Cases

The backing `Handle` is an untyped object, so correctness depends on the associated share/file store. The mutable `Path` can diverge from file-store state if rename paths are not updated consistently.

## Test Signals

Open/close tests should assert path, share, access, and timestamp reporting through session information.

Source-read signal: reviewed the complete local source file for this item.
