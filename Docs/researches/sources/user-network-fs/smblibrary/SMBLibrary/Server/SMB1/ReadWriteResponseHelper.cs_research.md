# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/ReadWriteResponseHelper.cs

## Purpose

Builds SMB1 read, read-andx, write, write-andx, and flush responses against open file-store handles.

## Important APIs, Types, And Functions

Methods validate FIDs and share access, call `ReadFile`, `WriteFile`, or `FlushFileBuffers`, map EOF for ReadAndX, set returned counts/data, and produce error responses on failure.

## Control Flow

ReadAndX honors `LargeRead` for filesystem shares by using `MaxCountLarge`; EOF is converted to success with zero data for Windows/JCIFS compatibility. Write methods return written counts. Flush with FID `0xFFFF` currently returns success without scanning PID-owned opens.

## State And Persistence Behavior

Reads and writes persistent file content through `INTFileStore`. Session open-file state is read but not mutated.

## Dependencies And Integration Points

Uses SMB1 read/write/flush command types, `FileSystemShare` access checks, and file-store read/write/flush APIs.

## Risks And Edge Cases

FID `0xFFFF` flush is effectively a no-op despite the comment requiring PID-wide flush. Access checks are share-type dependent. Count casts to 16-bit in legacy write/read responses can truncate large counts.

## Test Signals

Test invalid FID, access denied, EOF mapping, large read selection, short writes, named-pipe read/write behavior, and flush-all semantics.

Source-read signal: reviewed the complete local source file for this item.
